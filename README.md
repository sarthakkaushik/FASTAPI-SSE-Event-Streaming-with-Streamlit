# FastAPI SSE Progress with Streamlit Frontend (Managed by uv) 🚀

This project demonstrates real-time progress updates for simulated long-running tasks using Server-Sent Events (SSE). It features a FastAPI backend streaming progress and a Streamlit frontend visualizing it, with dependencies managed efficiently by `uv`.

The FastAPI backend simulates sequential tasks (sum, multiply, divide) and sends `progress` and `complete` events via SSE. The Streamlit app connects to this stream, updates a native progress bar (`st.progress`) and status messages in real-time, leveraging the exact dependencies specified in `pyproject.toml` and locked in `uv.lock` for reproducible environments.

## ✨ Features

*   **FastAPI Backend:**
    *   Simulates a multi-step background task using `asyncio`.
    *   Provides an SSE endpoint (`/stream-progress`) via `StreamingResponse`.
    *   Sends `progress` and `complete` event types.
    *   Handles basic client disconnects.
*   **Streamlit Frontend:**
    *   Connects to the FastAPI SSE endpoint using `requests` and `sseclient-py`.
    *   Updates `st.progress` bar and status messages (`st.info`, `st.success`, etc.) live.
    *   Displays final results and task summary.
    *   Handles connection errors.
*   **Dependency Management:**
    *   Uses `uv` for fast virtual environment creation and package installation.
    *   Dependencies defined in `pyproject.toml`.
    *   Reproducible environment ensured by `uv.lock`.

## 📸 Demo (Conceptual)

*(Imagine a GIF or screenshot here showing the Streamlit app with the progress bar filling up and status text changing.)*

1.  User clones the project and installs dependencies using `uv sync`.
2.  User runs the FastAPI backend and then the Streamlit frontend.
3.  User clicks "Start Task and Monitor Progress" in the Streamlit app.
4.  The progress bar and status text update dynamically, reflecting the backend task progress (~33%, ~66%, 100%).
5.  The task completes, showing a final result and summary.

## 📋 Requirements

*   **Python:** 3.8+ (Recommended for `uv`)
*   **uv:** A fast Python package installer and project manager. If you don't have it, install it globally first. See [official `uv` installation instructions](https://github.com/astral-sh/uv#installation).
    *   *Example (macOS/Linux):* `curl -LsSf https://astral.sh/uv/install.sh | sh`
    *   *Example (Windows PowerShell):* `irm https://astral.sh/uv/install.ps1 | iex`
    *   *Verify:* `uv --version`
*   **Git:** To clone the repository.

## ⚙️ Installation (using `uv` and provided files)

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/sarthakkaushik/FASTAPI-SSE-Event-Streaming-with-Streamlit.git 
    cd <your-project-directory-name>
    ```

2.  **Create and Activate Virtual Environment:**
    Use `uv` to create a virtual environment (it will likely create one named `.venv` by default).
    ```bash
    uv venv
    ```
    Activate the newly created environment:
    ```bash
    # On Windows (Command Prompt/PowerShell)
    .\.venv\Scripts\activate

    # On macOS/Linux (Bash/Zsh)
    source .venv/bin/activate
    ```
    *(Your terminal prompt should now indicate you are inside the virtual environment, e.g., `(.venv) ...`)*

3.  **Install Dependencies:**
    Use `uv sync` to install the exact dependencies specified in `pyproject.toml` and locked in `uv.lock`. This ensures you have the precise environment the project was developed with.
    ```bash
    uv sync
    ```
    `uv` will efficiently install all required packages.

## 🚀 Usage

You need two terminals open, both navigated to the project directory and with the virtual environment activated.

1.  **Terminal 1: Start the FastAPI Backend:**
    Make sure the `(.venv)` virtual environment is active.
    ```bash
    python main_progress.py
    ```
    The server should start, listening on `http://127.0.0.1:8000`.

2.  **Terminal 2: Start the Streamlit Frontend:**
    Make sure the `(.venv)` virtual environment is also active in this terminal.
    ```bash
    streamlit run streamlit_app.py
    ```
    Streamlit will provide a URL (usually `http://localhost:8501`) and open it in your browser.

3.  **Interact with the App:**
    *   In the Streamlit web page, click the "Start Task and Monitor Progress" button.
    *   Watch the progress bar fill up and status messages change in real-time!

## 🛠️ How it Works

1.  **Streamlit Request:** Clicking the button triggers a GET request to `/stream-progress` on the FastAPI backend.
2.  **FastAPI SSE Stream:** The backend endpoint returns a `StreamingResponse` powered by an `async` generator.
3.  **Backend Tasks & Events:** The generator runs simulated tasks (`sum`, `multiply`, `divide`) and `yield`s SSE formatted events (`event: progress`, `event: complete`) after each step.
4.  **Streamlit Event Consumption:** The frontend uses `sseclient-py` to listen to the event stream.
5.  **UI Updates:** Received events trigger updates to Streamlit elements (`st.progress`, `st.info`, `st.success`) on the frontend without page reloads.

## 📁 File Structure