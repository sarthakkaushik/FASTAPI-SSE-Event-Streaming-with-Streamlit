from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import asyncio, time

app = FastAPI()

# Async generator that yields five numbers
async def number_stream():
    for i in range(1, 6):
        yield {"event": "number", "data": i}
        await asyncio.sleep(1)

@app.get("/numbers")
async def numbers(request: Request):
    # Automatic heartbeat every 15 s prevents timeouts
    return EventSourceResponse(number_stream(), ping=15)
