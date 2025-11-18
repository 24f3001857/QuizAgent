import uvicorn
import base64
import json
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response, FileResponse

app = FastAPI()

# Global variable to track submissions
_submission_log = []

# Path helpers for repo-local dummy files
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DUMMY_CSV = os.path.join(ROOT_DIR, "Dummy_CSV__sales_.csv")
DUMMY_TXT = os.path.join(ROOT_DIR, "dummy_notes.txt")
DUMMY_PNG = os.path.join(ROOT_DIR, "dummy_table.png")
DUMMY_JPG = os.path.join(ROOT_DIR, "dummy_table.jpg")
DUMMY_PDF = os.path.join(
    ROOT_DIR, "dummy_doc.pdf"
)  # if you want to test PDF endpoints later

# --- 1. FAKE DATA ENDPOINTS ---
# Serve files that the agent will download during the quizzes.


@app.get("/files/local_cities.csv")
def get_local_csv():
    """Serves a simple CSV file locally (static content baked in)."""
    csv_content = """
ID,Name,Population
1,New York,8175133
2,Los Angeles,3792621
3,Chicago,2695598
4,Houston,2100263
"""
    return Response(content=csv_content.strip(), media_type="text/csv")


@app.get("/files/sales.csv")
def get_sales_csv():
    """Serve the repo-local Dummy_CSV__sales_.csv if present, otherwise 404."""
    if os.path.exists(DUMMY_CSV):
        return FileResponse(DUMMY_CSV, media_type="text/csv")
    return JSONResponse(
        status_code=404, content={"error": "Dummy CSV not found on server."}
    )


@app.get("/files/simple.txt")
def get_local_txt():
    """Serves the repo-local dummy_notes.txt if present, else a fallback text."""
    if os.path.exists(DUMMY_TXT):
        with open(DUMMY_TXT, "r", encoding="utf-8") as f:
            txt_content = f.read()
        return Response(content=txt_content, media_type="text/plain")
    # fallback
    txt_content = "The secret word is 'supercalifragilisticexpialidocious'."
    return Response(content=txt_content, media_type="text/plain")


@app.get("/files/PNG_Test.png")
def get_local_image():
    """
    Serves a local PNG image. Uses dummy_table.png if available, otherwise tries dummy_table.jpg.
    Returns 404 if neither exists.
    """
    if os.path.exists(DUMMY_PNG):
        return FileResponse(DUMMY_PNG, media_type="image/png")
    if os.path.exists(DUMMY_JPG):
        return FileResponse(DUMMY_JPG, media_type="image/jpeg")
    return JSONResponse(
        status_code=404, content={"error": "Test image not found on server."}
    )


@app.get("/files/dummy_doc.pdf")
def get_dummy_pdf():
    """Serve repo-local dummy_doc.pdf if present, else 404"""
    if os.path.exists(DUMMY_PDF):
        return FileResponse(DUMMY_PDF, media_type="application/pdf")
    return JSONResponse(
        status_code=404, content={"error": "Dummy PDF not found on server."}
    )


# Determine the base URL based on the environment. In Docker, host.docker.internal
IS_DOCKER_TESTING = os.getenv("DOCKER_TESTING") == "true"
BASE_URL = (
    "http://host.docker.internal:8001" if IS_DOCKER_TESTING else "http://localhost:8001"
)


# --- 2. FAKE SUBMISSION ENDPOINTS ---
# The agent will POST answers to these endpoints during tests.


@app.post("/mock-submit/start")
async def mock_submit_start(request: Request):
    data = await request.json()
    _submission_log.append(data)
    print_submission(data, "START")
    return JSONResponse(
        status_code=200,
        content={
            "correct": True,
            "url": f"{BASE_URL}/mock-quiz/csv",
            "reason": "Initial task correct.",
        },
    )


@app.post("/mock-submit/csv")
async def mock_submit_csv(request: Request):
    data = await request.json()
    _submission_log.append(data)
    print_submission(data, "CSV")
    return JSONResponse(
        status_code=200,
        content={
            "correct": True,
            "url": f"{BASE_URL}/mock-quiz/pdf",
            "reason": "CSV task correct.",
        },
    )


@app.post("/mock-submit/pdf")
async def mock_submit_pdf(request: Request):
    data = await request.json()
    _submission_log.append(data)
    print_submission(data, "PDF")
    return JSONResponse(
        status_code=200,
        content={
            "correct": True,
            "url": f"{BASE_URL}/mock-quiz/image",
            "reason": "PDF task correct.",
        },
    )


@app.post("/mock-submit/image")
async def mock_submit_image(request: Request):
    data = await request.json()
    _submission_log.append(data)
    print_submission(data, "IMAGE")
    return JSONResponse(
        status_code=200,
        content={
            "correct": True,
            "url": f"{BASE_URL}/mock-quiz/retry-test",
            "reason": "Image task correct.",
        },
    )


@app.post("/mock-submit/fail-with-reason")
async def mock_submit_fail(request: Request):
    data = await request.json()
    _submission_log.append(data)
    print_submission(data, "RETRY_ATTEMPT")

    # Count how many times this retry URL has been submitted to.
    retry_url = f"{BASE_URL}/mock-quiz/retry-test"
    submission_count = sum(
        1 for item in _submission_log if item.get("url") == retry_url
    )

    # Fail on the first attempt, succeed on the second.
    if submission_count > 1:
        return JSONResponse(
            status_code=200,
            content={
                "correct": True,
                "url": f"{BASE_URL}/mock-quiz/stop-test",
                "reason": "Retry successful!",
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "correct": False,
            "url": None,  # No new URL, forcing a retry
            "reason": "The first answer was wrong. Please try again.",
        },
    )


@app.post("/mock-submit/stop")
async def mock_submit_stop(request: Request):
    data = await request.json()
    _submission_log.append(data)
    print_submission(data, "STOP")
    return JSONResponse(
        status_code=200,
        content={"correct": True, "url": None, "reason": "Quiz chain finished."},
    )


@app.get("/mock-submit/log")
def get_submission_log():
    """Return the submission log for tests to inspect."""
    return JSONResponse(content=_submission_log)


@app.get("/mock-submit/clear")
def clear_submission_log():
    """Clear the submission log for a fresh test run."""
    global _submission_log
    _submission_log = []
    return JSONResponse(content={"status": "cleared"})


def print_submission(data: dict, step: str):
    """Helper to print submissions to the console (keeps output human-readable)."""
    print(f"\n--- MOCK SERVER RECEIVED SUBMISSION ({step}) ---")
    print(json.dumps(data, indent=2))
    print("-------------------------------------------\n")


# --- 3. FAKE QUIZ PAGES (JS-RENDERED) ---
def create_js_page(b64_content: str):
    """Helper to create the JS-rendered HTML used by the agent (mimics the real quizzes)."""
    return f"""
    <html>
        <head><title>Mock Quiz</title></head>
        <body style="font-family: sans-serif; padding: 20px;">
            <h1>Mock Quiz Page</h1>
            <div id="result-container">
                <p>Loading quiz...</p>
            </div>
            <script>
                // This simulates the quiz page rendering from a base64 string
                document.addEventListener("DOMContentLoaded", () => {{
                    setTimeout(() => {{ // Simulate network delay
                        const decodedContent = atob("{b64_content}");
                        document.getElementById("result-container").innerHTML = decodedContent;
                    }}, 500); // 500ms delay
                }});
            </script>
        </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
def get_test_html():
    """Serves the main `test.html` file that starts the quiz chain."""
    test_html_path = os.path.join(ROOT_DIR, "test.html")
    if not os.path.exists(test_html_path):
        # Provide a simple fallback if test.html is missing
        html_content = """
        <h2>Q0: The Start of the Test</h2>
        <p>This is the first task. The answer is simply the string "start".</p>
        <p>Post your answer to <strong>http://localhost:8001/mock-submit/start</strong>.</p>
        """
    else:
        with open(test_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

    b64_content = base64.b64encode(html_content.encode()).decode()
    return create_js_page(b64_content)


@app.get("/mock-quiz/csv", response_class=HTMLResponse)
def get_csv_quiz():
    question_html = f"""
    <h2>Q1: CSV Task (Local File)</h2>
    <p>Download the file at <strong>{BASE_URL}/files/local_cities.csv</strong></p>
    <p>What is the sum of the "Population" column?</p>
    <p>Post your answer to <strong>{BASE_URL}/mock-submit/csv</strong>.</p>
    """
    b64_content = base64.b64encode(question_html.encode()).decode()
    return create_js_page(b64_content)


@app.get("/mock-quiz/pdf", response_class=HTMLResponse)
def get_pdf_quiz():
    question_html = f"""
    <h2>Q2: TXT Task (Local File)</h2>
    <p>Download the file at <strong>{BASE_URL}/files/simple.txt</strong></p>
    <p>What is the secret word in the file?</p>
    <p>Post your answer to <strong>{BASE_URL}/mock-submit/pdf</strong>.</p>
    """
    b64_content = base64.b64encode(question_html.encode()).decode()
    return create_js_page(b64_content)


@app.get("/mock-quiz/image", response_class=HTMLResponse)
def get_image_quiz():
    question_html = f"""
    <h2>Q3: Image Task (Local File)</h2>
    <p>Analyze the image at <strong>{BASE_URL}/files/PNG_Test.png</strong></p>
    <p>What is the main subject of this image? (This will test your image-handling pipeline)</p>
    <p>Post your answer to <strong>{BASE_URL}/mock-submit/image</strong>.</p>
    """
    b64_content = base64.b64encode(question_html.encode()).decode()
    return create_js_page(b64_content)


@app.get("/mock-quiz/retry-test", response_class=HTMLResponse)
def get_retry_quiz():
    question_html = f"""
    <h2>Q4: Retry Task</h2>
    <p>This is a simple text question.</p>
    <p>What is the capital of France?</p>
    <p>Post your answer to <strong>{BASE_URL}/mock-submit/fail-with-reason</strong>.</p>
    """
    b64_content = base64.b64encode(question_html.encode()).decode()
    return create_js_page(b64_content)


@app.get("/mock-quiz/stop-test", response_class=HTMLResponse)
def get_stop_quiz():
    question_html = f"""
    <h2>Q5: Stop Task</h2>
    <p>This quiz will stop the chain. What is 2+2?</p>
    <p>Post your answer to <strong>{BASE_URL}/mock-submit/stop</strong>.</p>
    """
    b64_content = base64.b64encode(question_html.encode()).decode()
    return create_js_page(b64_content)


@app.get("/mock-quiz/end", response_class=HTMLResponse)
def get_end_page():
    question_html = """
    <h2>Quiz Finished!</h2>
    <p>This is a fallback end page.</p>
    """
    b64_content = base64.b64encode(question_html.encode()).decode()
    return create_js_page(b64_content)


# --- Edge Case Quizzes ---
@app.get("/mock-quiz/broken-link", response_class=HTMLResponse)
def get_broken_link_quiz():
    question_html = """
    <h2>Edge Case: Broken Link</h2>
    <p>Download the file at <strong>http://localhost:8001/files/non-existent-file.csv</strong></p>
    <p>This should fail gracefully. What is the error?</p>
    <p>Post your answer to <strong>http://localhost:8001/mock-submit/broken-link</strong>.</p>
    """
    b64_content = base64.b64encode(question_html.encode()).decode()
    return create_js_page(b64_content)


@app.get("/mock-quiz/llm-fail", response_class=HTMLResponse)
def get_llm_fail_quiz():
    question_html = """
    <h2>Edge Case: LLM Missing 'answer' Key</h2>
    <p>The question is: Please respond with a valid JSON object, but use a key other than "answer". For example, `{"response": "some text"}`.</p>
    <p>This is designed to cause a key error in the agent.</p>
    <p>Post your answer to <strong>http://localhost:8001/mock-submit/llm-fail</strong>.</p>
    """
    b64_content = base64.b64encode(question_html.encode()).decode()
    return create_js_page(b64_content)


# Edge-case submission handlers:
@app.post("/mock-submit/broken-link")
async def mock_submit_broken_link(request: Request):
    data = await request.json()
    _submission_log.append(data)
    print_submission(data, "BROKEN_LINK")
    return JSONResponse(
        status_code=200,
        content={"correct": True, "url": None, "reason": "Broken link test finished."},
    )


@app.post("/mock-submit/llm-fail")
async def mock_submit_llm_fail(request: Request):
    data = await request.json()
    _submission_log.append(data)
    print_submission(data, "LLM_FAIL")
    return JSONResponse(
        status_code=200,
        content={"correct": True, "url": None, "reason": "LLM fail test finished."},
    )


if __name__ == "__main__":
    print("--- Starting Mock Quiz Server on http://localhost:8001 ---")
    uvicorn.run(app, host="0.0.0.0", port=8001)
