"""Image Generator crew.

Agent LLM: databricks/databricks-gpt-5-4
Image tool: DallETool (uses OPENAI_API_KEY env var internally)
Output: saved to outputs/<uuid>.png; SSE emits [IMAGE] /outputs/<uuid>.png
"""
import queue
import threading
import uuid
from pathlib import Path
from typing import Type

import requests
from crewai import Agent, Task, Crew, LLM
from crewai_tools import DallETool
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from utils import capture_to_queue

load_dotenv()

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

llm = LLM(model="databricks/databricks-gpt-5-4")


# ---------------------------------------------------------------------------
# Custom download tool that saves to outputs/ and tracks the saved path
# ---------------------------------------------------------------------------

class DownloadImageInput(BaseModel):
    image_url: str = Field(..., description="The URL of the image to download.")


class DownloadImageTool(BaseTool):
    name: str = "Image Downloader Tool"
    description: str = "Downloads an image from a URL and saves it to disk."
    args_schema: Type[BaseModel] = DownloadImageInput
    saved_path: str = Field(default="", exclude=True)

    def _run(self, image_url: str) -> str:
        filename = f"{uuid.uuid4()}.png"
        filepath = OUTPUTS_DIR / filename
        try:
            response = requests.get(image_url, stream=True, timeout=60)
            response.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            self.saved_path = f"/outputs/{filename}"
            return f"Image saved to {filepath}"
        except Exception as exc:
            return f"Failed to download image: {exc}"


# ---------------------------------------------------------------------------
# Thread entry-point
# ---------------------------------------------------------------------------

def run_image_crew(initial_prompt: str, output_queue: queue.Queue) -> None:
    download_tool = DownloadImageTool()

    with capture_to_queue(output_queue):
        try:
            dalle_tool = DallETool(
                model="dall-e-3",
                size="1024x1024",
                quality="standard",
                n=1,
            )

            prompt_improver = Agent(
                llm=llm,
                role="Prompt Improver",
                backstory="An AI agent that enhances image generation prompts to be more detailed and vivid.",
                goal="Improve text prompts for optimal DALL-E image generation.",
                verbose=True,
            )

            image_generator = Agent(
                llm=llm,
                role="Image Generator",
                backstory="An AI agent that generates images using DALL-E and downloads them locally.",
                goal="Generate images from enhanced prompts and save them to disk.",
                tools=[dalle_tool, download_tool],
                verbose=True,
            )

            enhance_task = Task(
                description=f"Improve this prompt: '{initial_prompt}' to make it more descriptive for image generation.",
                expected_output='Enhanced prompt as: "image_description": "<enhanced prompt>"',
                agent=prompt_improver,
            )

            generate_task = Task(
                description="Generate an image from the enhanced prompt using DALL-E.",
                expected_output="image_url: URL of the generated image",
                agent=image_generator,
            )

            download_task = Task(
                description="Download the generated image from the URL using the Image Downloader Tool.",
                expected_output="Confirmation that the image was downloaded and saved locally.",
                agent=image_generator,
            )

            crew = Crew(
                agents=[prompt_improver, image_generator],
                tasks=[enhance_task, generate_task, download_task],
                verbose=True,
            )

            result = crew.kickoff(inputs={"initial_prompt": initial_prompt})

            if download_tool.saved_path:
                output_queue.put(f"[IMAGE] {download_tool.saved_path}")

            output_queue.put("__DONE__")
            output_queue.put(result.raw)

        except Exception as exc:
            output_queue.put(f"ERROR: {exc}")
            output_queue.put("__DONE__")
            output_queue.put(f"Crew failed: {exc}")


def start_image_crew(initial_prompt: str) -> queue.Queue:
    q: queue.Queue = queue.Queue()
    threading.Thread(
        target=run_image_crew,
        args=(initial_prompt, q),
        daemon=True,
    ).start()
    return q
