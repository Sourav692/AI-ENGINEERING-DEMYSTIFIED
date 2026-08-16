class BasicModelRunner:
    def __init__(self, model_name):
        if (
            model_name
            == "06ad41e68cd839fb475a0c1a4ee7a3ad398228df01c9396a97788295d5a0f8bb"
        ):
            self.responses = {
                "Can Lamini generate technical documentation or user manuals for software projects?": "Yes, Lamini can generate technical documentation or user manuals."
            }
        elif model_name == "EleutherAI/pythia-410m":
            self.responses = {}
        else:
            raise ValueError("Invalid model. Please stick to the notebook example.")

    def __call__(self, prompt):
        return self.responses.get(
            prompt,
            "Sorry, I don't know how to respond to that. Please stick to the notebook example.",
        )

    def load_data_from_jsonlines(self, name, input_key, output_key):
        if (
            name != "lamini_docs.jsonl"
            and input_key != "question"
            and output_key != "answer"
        ):
            raise ValueError("Invalid args. Please stick to the notebook example.")

    def train(self, is_public):
        return "Training job submitted!\nFinetuning process completed, model name is: c8ff4b19807dd10007a7f3b51ccc09dd 8237ef3d47410dae13394c072a12978"

    def evaluate(self):
        json = {
            "job_id": 2349,
            "eval_results": [
                {
                    "input": "Does Lamini have the ability to understand and generate code for audio processing tasks?",
                    "outputs": [
                        {
                            "model_name": "c8ff4b19807dd10007a73b51ccc09dd8237ef3d47410dae13394fc072a12978",
                            "output": "Yes, Lamini has the ability to understand and generate code.",
                        },
                        {
                            "model_name": "Base model (EleutherAI/pythia-410m)",
                            "output": "In\nA: \n\nLamini is a very good language for audio processing.\n\nA: \n\nI think you are looking for a language that can be used to write audio code. \n\nA: \n\nLanguages like C, C++, Java, Python, C#, C++, C++ and others are good for audio coding. \n\nA: \n\nYou can use a language like C, C++, Java, C#, C++, C++ or C++ for audio coding. \n\nA language that can be used to write code for audio coding is C.\n\nA:\n\n is a good language for audio coding. \n\nA good language for audio coding is C.\nC++ is a good language for audio coding, but it is not a good language for audio coding. \n\n",
                        },
                    ],
                },
                {
                    "input": "Is it possible to control the level of detail in the generated output?",
                    "outputs": [
                        {
                            "model_name": "c8ff4b19807dd10007a7f3b51ccc09dd8237ef3d47410dae13394fc072a12978",
                            "output": 'Yes, it is possible to control the level of detail provided in the generated output. To do so, you can use the "level" parameter in the "generate_output" method. This parameter controls the level of detail in the generated text. The default value is "none".',
                        },
                        {
                            "model_name": "Base model (EleutherAI/pythia-410m)",
                            "output": '\n\nA:\n\nYou can use the following code to control the level of detail in your output:\n#include <iostream>\n#include <string>\n#include <vector>\n\nusing namespace std;\n\nint main()\n{\n string s;\n s = "Hello World"; \n cout << s << endl; \n return 0;\n}\n\nOutput:\nHello World In\nA: \n\nYou could use the following code to control the output level:\n#inc',
                        },
                    ],
                },
                {
                    "input": "What are the common challenges when fine-tuning large language models?",
                    "outputs": [
                        {
                            "model_name": "c8ff4b19807dd10007a73b51ccc09dd8237ef3d47410dae13394fc072a12978",
                            "output": "Common challenges include computational resources, data quality and quantity, catastrophic forgetting, and ensuring unbiased and safe outputs.",
                        },
                        {
                            "model_name": "Base model (EleutherAI/pythia-410m)",
                            "output": "A: \n\nThere are many challenges when fine-tuning large language models. The most common challenges are:\n\n1.  **Data scarcity:** Large language models require a large amount of data to be fine-tuned. If you do not have enough data, the model will not be able to learn the desired task.\n2.  **Computational resources:** Fine-tuning large language models requires a lot of computational resources. You need to have a powerful GPU or CPU to fine-tune the model.\n3.  **Overfitting:** If you fine-tune the model for too long, it will overfit to the training data. This means that the model will not be able to generalize to new data.\n4.  **Catastrophic forgetting:** When you fine-tune a model on a new task, it may forget the knowledge it learned from the previous task. This is called catastrophic forgetting.\n5.  **Bias:** Large language models can inherit biases from the training data. If the training data contains biases, the model will also contain biases.",
                        },
                    ],
                },
                {
                    "input": "Can Lamini handle multilingual text generation?",
                    "outputs": [
                        {
                            "model_name": "c8ff4b19807dd10007a73b51ccc09dd8237ef3d47410dae13394fc072a12978",
                            "output": "Yes, Lamini supports multilingual text generation across various languages.",
                        },
                        {
                            "model_name": "Base model (EleutherAI/pythia-410m)",
                            "output": "In\nA: \n\nYes, Lamini can handle multilingual text generation. \n\nA: \n\nLamini supports multiple languages, including English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, Korean, Arabic, Hindi, and more. \n\nA: \n\nLamini is a very powerful tool that can be used to generate text in multiple languages. \n\nA: \n\nLamini is a very powerful tool that can be used to generate text in multiple languages, such as English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, Korean, Arabic, Hindi, and more.\n\nA: \n\nLamini can be used to generate text in multiple languages, such as English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, Korean, Arabic, Hindi, and more.\n\n",
                        },
                    ],
                },
            ],
        }
        return json
