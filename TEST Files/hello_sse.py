from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio,datetime,itertools

app=FastAPI()

async def event_generator():
    """
    Simulate an event stream by yielding a new event every second.
    """
    for i in itertools.count():
        # Simulate a delay
        yield f"data: {datetime.datetime.utcnow().isoformat()}#i\n\n"
        await asyncio.sleep(1)

@app.get("/time")
async def time_stream():
    """
    Endpoint to stream the current time as an event stream.
    """
    return StreamingResponse(event_generator(), media_type="text/event-stream")