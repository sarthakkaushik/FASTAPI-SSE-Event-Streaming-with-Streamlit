import asyncio
import json
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# HTML for progress bar (remains the same as your example)
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>SSE Progress Example</title>
        <style>
            /* Optional: make progress bar more visible */
            progress {
                width: 100%;
                height: 25px;
            }
        </style>
    </head>
    <body>
        <h1>Sequential Task Progress</h1>
        <progress id="progress-bar" value="0" max="100"></progress>
        <div id="status">Status: Waiting to start...</div>
        <div id="result">Result: Not finished</div>
        <script>
            const progressBar = document.getElementById('progress-bar');
            const statusElement = document.getElementById('status');
            const resultElement = document.getElementById('result');

            console.log("Initializing EventSource for /stream-progress");
            const eventSource = new EventSource('/stream-progress');

            // Listener for 'progress' updates
            eventSource.addEventListener('progress', function(event) {
                try {
                    const data = JSON.parse(event.data);
                    progressBar.value = data.percent;
                    statusElement.textContent = `Status: ${data.message} (${data.percent}%)`;
                    console.log("Progress update:", data);
                } catch (e) {
                    console.error("Error parsing progress data:", e, event.data);
                    statusElement.textContent = "Status: Error parsing update.";
                }
            });

            // Listener for the 'complete' event
            eventSource.addEventListener('complete', function(event) {
                 try {
                    const data = JSON.parse(event.data);
                    progressBar.value = 100; // Ensure progress bar is full
                    statusElement.textContent = "Status: Task Completed!";
                    resultElement.textContent = `Result: ${data.result}`;
                    console.log("Task complete:", data);
                    eventSource.close(); // Close the connection once task is done
                    console.log("SSE connection closed by client upon completion.");
                } catch (e) {
                    console.error("Error parsing complete data:", e, event.data);
                    statusElement.textContent = "Status: Error parsing completion update.";
                    eventSource.close();
                }
            });

            eventSource.onerror = function(error) {
                statusElement.textContent = "Status: Error connecting (see console)";
                console.error("EventSource failed:", error, "State:", eventSource.readyState);
                // Don't close here if you want browser's auto-reconnect to try
                if (eventSource.readyState === EventSource.CLOSED) {
                    console.log("SSE connection definitely closed.");
                } else {
                    console.log("SSE error, browser might attempt to reconnect.");
                }
            };

            eventSource.onopen = function() {
                statusElement.textContent = "Status: Connected, task starting...";
                console.log("Connection to SSE stream opened.");
                 progressBar.value = 0; // Reset progress on open
                 resultElement.textContent = "Result: Not finished";
            };

            window.onbeforeunload = function() {
                if (eventSource && eventSource.readyState !== EventSource.CLOSED) {
                    eventSource.close();
                    console.log("SSE Connection closed by window unload.");
                }
            };
        </script>
    </body>
</html>
"""

@app.get("/")
async def get_index_page():
    """Serve the HTML page for the SSE client."""
    return HTMLResponse(content=html)

# --- Worker Functions (They just do work, no SSE yielding) ---
async def sum_operation():
    """Simulates the 'sum' part of the task."""
    logger.info("Starting sum_operation...")
    await asyncio.sleep(2) # Simulate work for 2 seconds
    logger.info("sum_operation finished.")
    return "Sum operation successful"

async def multiply_operation():
    """Simulates the 'multiply' part of the task."""
    logger.info("Starting multiply_operation...")
    await asyncio.sleep(3) # Simulate work for 3 seconds
    logger.info("multiply_operation finished.")
    return "Multiply operation successful"

async def divide_operation():
    """Simulates the 'divide' part of the task."""
    logger.info("Starting divide_operation...")
    await asyncio.sleep(1.5) # Simulate work for 1.5 seconds
    logger.info("divide_operation finished.")
    return "Divide operation successful"

# --- The Main SSE Generator ---
async def main_task_sse_generator(request: Request):
    """
    Main generator that orchestrates tasks and sends SSE progress updates.
    """
    logger.info("Client connected. Starting main task sequence.")
    total_tasks = 3 # We have sum, multiply, divide

    try:
        # --- Task 1: Sum ---
        if await request.is_disconnected():
            logger.warning("Client disconnected before sum_operation.")
            return # Stop generating if client disconnected

        sum_result = await sum_operation()
        progress_data_sum = {
            "percent": int(1/total_tasks * 100),
            "message": f"Sum Operation Complete. Status: {sum_result}"
        }
        yield f"event: progress\ndata: {json.dumps(progress_data_sum)}\n\n"
        logger.info(f"Sent progress after sum: {progress_data_sum}")


        # --- Task 2: Multiply ---
        if await request.is_disconnected():
            logger.warning("Client disconnected before multiply_operation.")
            return

        multiply_result = await multiply_operation()
        progress_data_multiply = {
            "percent": int(2/total_tasks * 100),
            "message": f"Multiply Operation Complete. Status: {multiply_result}"
        }
        yield f"event: progress\ndata: {json.dumps(progress_data_multiply)}\n\n"
        logger.info(f"Sent progress after multiply: {progress_data_multiply}")


        # --- Task 3: Divide ---
        if await request.is_disconnected():
            logger.warning("Client disconnected before divide_operation.")
            return

        divide_result = await divide_operation()
        progress_data_divide = {
            "percent": int(3/total_tasks * 100), # Should be 100%
            "message": f"Divide Operation Complete. Status: {divide_result}"
        }
        yield f"event: progress\ndata: {json.dumps(progress_data_divide)}\n\n"
        logger.info(f"Sent progress after divide: {progress_data_divide}")


        # --- All Tasks Complete ---
        if await request.is_disconnected():
            logger.warning("Client disconnected just before sending completion.")
            return

        completion_data = {
            "result": "All operations (Sum, Multiply, Divide) completed successfully!",
            "summary": {
                "sum": sum_result,
                "multiply": multiply_result,
                "divide": divide_result
            }
        }
        yield f"event: complete\ndata: {json.dumps(completion_data)}\n\n"
        logger.info("Sent final completion message.")

    except asyncio.CancelledError:
        # This exception is raised if the client disconnects *during* an await call
        # or if the task is cancelled for other reasons by FastAPI/Uvicorn.
        logger.warning("Task stream was cancelled (e.g., client disconnected during an await).")
    except Exception as e:
        logger.error(f"An unexpected error occurred in the SSE generator: {e}", exc_info=True)
        # Optionally, send an error event to the client if the connection is still alive
        try:
            error_payload = {"error": "An unexpected server error occurred.", "details": str(e)}
            yield f"event: error\ndata: {json.dumps(error_payload)}\n\n" # Assuming client handles 'error' event
        except Exception as send_err:
            logger.error(f"Failed to send error event to client: {send_err}")
    finally:
        logger.info("Main task SSE generator finished.")


@app.get("/stream-progress")
async def stream_overall_progress(request: Request):
    """
    Endpoint that returns the SSE stream for overall task progress.
    Uses StreamingResponse with the main_task_sse_generator.
    """
    # You could add initial checks here if needed, e.g., authentication.
    return StreamingResponse(main_task_sse_generator(request), media_type="text/event-stream")

if __name__ == "__main__":
    # Make sure the file name here matches your actual file name if it's not 'main_progress.py'
    # For example, if your file is my_sse_app.py, use "my_sse_app:app"
    uvicorn.run("main_progress:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
    # Changed "main_progress:app" to "main:app" assuming your file is called main.py or similar.
    # Adjust if your Python file has a different name.