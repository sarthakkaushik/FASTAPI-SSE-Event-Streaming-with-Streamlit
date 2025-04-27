import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse

app=FastAPI()

# Basic HTML page with JavaScript to connect to the SSE endpoint
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>SSE Basic Example</title>
    </head>
    <body>
        <h1>SSE Basic Counter</h1>
        <div id="sse-data">Waiting for data...</div>
        <script>
            const sseDataElement = document.getElementById('sse-data');
            // Create an EventSource object to connect to the SSE endpoint
            const eventSource = new EventSource('/stream'); // URL of our SSE endpoint

            // The 'onmessage' event is triggered for messages without a specific 'event:' field
            eventSource.onmessage = function(event) {
                // event.data contains the data sent from the server
                sseDataElement.innerHTML = `Received: ${event.data}`;
                console.log("Received data:", event.data);
            };

            // Optional: Handle errors
            eventSource.onerror = function(error) {
                sseDataElement.innerHTML = "Error connecting to SSE stream. Check console.";
                console.error("EventSource failed:", error);
                eventSource.close(); // Close the connection on error
            };

            // Optional: Handle the connection opening
            eventSource.onopen = function() {
                console.log("Connection to SSE stream opened.");
                sseDataElement.innerHTML = "Connection opened. Waiting for data...";
            };

            // Optional: Close the connection when the window is closed
            window.onbeforeunload = function() {
                eventSource.close();
                console.log("SSE Connection closed.");
            };
        </script>
    </body>
</html>
"""

@app.get("/")
async def get_index():
    """
    Serve the HTML page for the SSE client.
    """
    return HTMLResponse(content=html, status_code=200)

async def basic_event_generator():
    """
    Simulate an event stream by yielding a new event every second.
    """
    for i in range(1, 6):
        # Simulate a delay
        message = f"Hello! Count is {i}"
        yield f"data: {message}\n\n"
        print(f"Sent: {message}") # Server-side log
        await asyncio.sleep(1)

    yield f"data: Finished sending events.\n\n"
    print("Finished sending events.") # Server-side log


@app.get("/stream")
async def  stream_event(request: Request):
    """
    Endpoint that returns the SSE stream.
    Uses StreamingResponse with the generator.
    """
    return StreamingResponse(basic_event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    # Run the app with Uvicorn
    # Use reload=True for development so it restarts on code changes
    uvicorn.run("main_basic:app", host="0.0.0.0", port=8000, reload=True)