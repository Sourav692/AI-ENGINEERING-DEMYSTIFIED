# Coding Essentials for Agents

A comprehensive Python course covering the essential programming skills needed for building AI agents and LLM-based applications. Based on the [Analytics Vidhya course](https://courses.analyticsvidhya.com/courses/take/coding-essential-for-agents/downloads/60036869-course-handouts-updated-on-2025-10-27).

## Modules

### 1. Introduction to Python
Covers Python fundamentals — variables, operators, conditional statements, loops, functions, and best practices (PEP 8, PEP 257).

### 2. Working with Files and Databases
Hands-on with **NumPy**, **Pandas**, and **Matplotlib** for data analysis, plus database operations with **SQLite**, **MySQL**, and **PostgreSQL** using SQLAlchemy.

### 3. Working with APIs
Build web applications and REST APIs with **Flask**, including route handling, Jinja2 templates, and a Stock Market API project.

### 4. Working with LLMs
Integrate large language models using the **OpenAI** and **Google Gemini** APIs, call open-source models via **Hugging Face**, and run models locally with **Transformers**.

### 5. Multithreading, Multiprocessing and GIL
Understand Python's concurrency model — threads, processes, the Global Interpreter Lock, locks, queues, and shared memory.

### 6. Asyncio
Asynchronous programming with `async`/`await`, coroutines, background workers, daemons, race conditions, and deadlocks.

## Project Structure

```
├── 1. Introduction to Python/          # Jupyter notebooks — Python basics
├── 2. Working with Files and Databases/ # NumPy, Pandas, Matplotlib, SQL notebooks
│   └── docs/                           # Sample datasets (churn_prediction.csv)
├── 3. Working with APIs/
│   └── Flask Hands on/                 # Flask app notebooks + templates & static files
├── 4. Working with LLMs/               # OpenAI, Gemini, Hugging Face notebooks
├── 5. MultiThreading, MultiProcessing and GIL/  # Python scripts
├── 6. Asyncio/                         # Python scripts
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites

- Python 3.10+
- (Optional) MySQL / PostgreSQL instances for database modules
- (Optional) GPU with ~5 GB VRAM for running local LLMs

### Installation

```bash
# Clone the repository
git clone https://github.com/Sourav692/Coding_Essential_For_Agents.git
cd Coding_Essential_For_Agents

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

For the LLM modules, set your API keys:

```bash
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-gemini-key"
```

## Usage

**Jupyter notebooks** (Modules 1–4):

```bash
jupyter notebook
```

**Python scripts** (Modules 5–6):

```bash
python "5. MultiThreading, MultiProcessing and GIL/01_threading.py"
python "6. Asyncio/01_async_one.py"
```

## Technologies

| Category | Stack |
|---|---|
| Language | Python 3.10+ |
| Data Science | NumPy, Pandas, Matplotlib |
| Databases | SQLite, MySQL, PostgreSQL, SQLAlchemy |
| Web Framework | Flask |
| LLM APIs | OpenAI, Google Generative AI |
| Local LLMs | Hugging Face Transformers, PyTorch |
| Notebooks | Jupyter |

## License

This project is for educational purposes.
