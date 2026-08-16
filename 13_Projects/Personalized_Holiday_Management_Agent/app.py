from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from autogen_agentchat.messages import TextMessage
from holiday_management.teams.holiday_team import team

class PlanRequest(BaseModel):
    content: str
    source: str = "User"


app = FastAPI(title="Holiday Management API")



# serve static files from ./static
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})




@app.post("/plan")
async def plan(req: PlanRequest):
    try:
        task = TextMessage(content=req.content, source=req.source)
        result = await team.run(task=task)
        messages = [{"source": m.source, "content": m.content} for m in result.messages]
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)