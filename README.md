# LLM-Powered Quiz Solver Agent

## Overview

This project is a sophisticated, asynchronous FastAPI application designed to autonomously solve a series of online quizzes. It leverages a hybrid AI approach, using multiple large language models to understand questions, process various data formats, and find correct answers.

The agent can scrape web pages, extract text from documents like PDFs and CSVs, and analyze images to solve complex, multi-step data challenges.

## Features

- **Asynchronous Web Server**: Built with FastAPI for high-performance, non-blocking I/O.
- **Dynamic Web Scraping**: Uses Playwright to render JavaScript-heavy pages and extract content, mimicking a real user.
- **Hybrid AI Brain**:
    - **Groq LPU Inference Engine**: Utilizes the ultra-fast Llama 3 model via Groq for all text-based tasks (analyzing web text, PDFs, CSVs).
    - **Google Gemini 1.5 Flash**: Employs Google's powerful multimodal model to analyze and answer questions about images.
- **Intelligent Task Routing**: Automatically detects the type of data (text, image, PDF, etc.) and routes the task to the appropriate AI model.
- **Recursive Quiz Solving**: Capable of solving an entire chain of quizzes, automatically proceeding to the next URL upon a successful or directed submission.
- **Robust Error Handling**: Manages API failures and continues the quiz chain even if an answer is incorrect but a new URL is provided.
- **Dockerized**: Comes with a `Dockerfile` for easy containerization and deployment, including all necessary system dependencies.

## Architecture Flow

The application operates in a simple yet powerful loop for each quiz:

1.  **Receive Task**: The agent receives a POST request at the `/quiz` endpoint with a URL to a quiz.
2.  **Scrape Content**: It navigates to the URL with a headless browser (Playwright) and scrapes the fully rendered text content.
3.  **Detect Data Source**: The agent analyzes the scraped text to find links to external data files like PDFs, CSVs, or images.
4.  **Route to AI Model**:
    - If an **image** is detected, it's sent to **Google Gemini 1.5 Flash** along with the text prompt.
    - If a **text-based file** (PDF, CSV) or no file is detected, the context is sent to **Groq's Llama 3** model.
5.  **Get Answer**: The chosen AI model analyzes the context and question, returning the answer in the required JSON format.
6.  **Submit Answer**: The agent posts the answer to the submission URL specified on the quiz page.
7.  **Recurse**: If the submission response contains a new quiz URL, the agent calls itself to begin the process again on the new task.

## Setup and Installation

### 1. Prerequisites
- Python 3.10+
- Docker (for containerized deployment)

### 2. Installation
Clone the repository and navigate into the project directory.

```bash
git clone <repository-url>
cd LLMQuizer
```

Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
This project requires API keys for the AI services it uses. Create a `.env` file in the root of the project and add the following variables:

```
# .env file

# Your secret and email for the quiz platform
MY_EMAIL="your-email@example.com"
MY_SECRET="your_provided_secret"

# API key for Groq (https://console.groq.com/keys)
GROQ_API_KEY="gsk_..."

# API key for Google AI Studio (https://aistudio.google.com/app/apikey)
GOOGLE_API_KEY="AIza..."
```

## How to Run

### Local Development
To run the application locally for development, use `uvicorn`:

```bash
uvicorn main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

### Sending a Test Request
You can start a quiz-solving chain by sending a POST request to the `/quiz` endpoint.

```bash
curl -X POST http://127.0.0.1:8000/quiz \
-H "Content-Type: application/json" \
-d '{
    "email": "your-email@example.com",
    "secret": "your_provided_secret",
    "url": "https://initial-quiz-url.com"
}'
```

### Docker Deployment
The included `Dockerfile` is optimized for deployment on cloud platforms like Google Cloud Run.

Build the Docker image:

```bash
docker build -t llm-quiz-agent .
```

Run the Docker container:

```bash
docker run -p 8080:8080 --env-file .env llm-quiz-agent
```
The application will be accessible at `http://localhost:8080`.

```