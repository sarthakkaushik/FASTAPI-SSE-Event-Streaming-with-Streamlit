# --- START OF FILE streamlit_app.py ---
import streamlit as st
import requests
import sseclient
import json
import time

# --- Configuration ---
FASTAPI_BACKEND_URL = "http://127.0.0.1:8000"  # Adjust if your FastAPI runs elsewhere

st.set_page_config(page_title="Task Progress Viewer", layout="wide")

st.title("🚀 Real-time Task Progress from FastAPI")

st.markdown(f"""
This app connects to a FastAPI backend (`{FASTAPI_BACKEND_URL}`)
that performs a sequence of tasks and streams progress updates using Server-Sent Events (SSE).
""")

# --- Button to start the process ---
if st.button("Start Task and Monitor Progress", key="start_task"):

    # --- UI Placeholders ---
    # We create placeholders first, then update them within the SSE loop.
    st.info("Attempting to connect to the backend stream...")
    progress_bar_placeholder = st.empty()
    status_text_placeholder = st.empty()
    result_placeholder = st.empty()

    # Initialize UI elements
    progress_bar_placeholder.progress(0)
    status_text_placeholder.info("Status: Waiting for connection...")
    result_placeholder.empty() # Clear previous results if any

    try:
        # --- Connect to the SSE stream ---
        # Using requests with stream=True and wrapping with sseclient
        response = requests.get(f"{FASTAPI_BACKEND_URL}/stream-progress", stream=True, headers={'Accept': 'text/event-stream'})
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        client = sseclient.SSEClient(response)

        st.success("✅ Connected to the backend stream. Waiting for updates...")

        # --- Process events from the stream ---
        for event in client.events():
            # Heartbeat/keep-alive messages might be empty or just comments
            if not event.data:
                # You could add a st.spinner or log here if you want to see keep-alives
                # print("Received keep-alive or empty message")
                continue

            # Attempt to parse the data as JSON
            try:
                data = json.loads(event.data)
            except json.JSONDecodeError:
                st.warning(f"⚠️ Received non-JSON data: {event.data}")
                continue # Skip this event if it's not valid JSON

            # --- Handle 'progress' events ---
            if event.event == 'progress':
                percent = data.get("percent", 0)
                message = data.get("message", "Processing...")

                # Update Streamlit elements
                progress_bar_placeholder.progress(percent / 100.0) # st.progress expects 0.0 to 1.0
                status_text_placeholder.info(f"Status: {message} ({percent}%)")
                st.write(f"Received progress: {percent}% - {message}") # Optional: log updates

            # --- Handle 'complete' event ---
            elif event.event == 'complete':
                result = data.get("result", "Task finished successfully!")
                summary = data.get("summary", {}) # Get the summary if available

                # Update Streamlit elements to final state
                progress_bar_placeholder.progress(1.0) # Ensure bar is full
                status_text_placeholder.success("Status: Task Completed!")
                result_placeholder.success(f"**Result:** {result}")

                if summary:
                    st.subheader("Task Summary:")
                    st.json(summary) # Display the summary nicely

                st.balloons() # Fun celebration!
                st.write("Stream finished.")
                break # Exit the loop as the task is done

            # --- Handle potential custom 'error' events (if you added them) ---
            elif event.event == 'error':
                 error_msg = data.get("error", "Unknown error occurred.")
                 details = data.get("details", "")
                 progress_bar_placeholder.empty() # Remove progress bar on error
                 status_text_placeholder.error(f"Status: An error occurred!")
                 result_placeholder.error(f"**Error:** {error_msg}\nDetails: {details}")
                 st.write("Stream stopped due to error.")
                 break # Exit the loop on error

            # --- Handle any other message types (optional) ---
            else:
                 # This might catch default 'message' events if the server sends them
                 st.write(f"Received unhandled event type '{event.event}': {event.data}")


        # Close the connection after the loop finishes or breaks
        client.close()
        response.close() # Ensure the requests response is also closed
        st.write("Connection closed.")

    except requests.exceptions.ConnectionError as e:
        progress_bar_placeholder.empty()
        status_text_placeholder.empty()
        result_placeholder.error(
            f"❌ **Connection Error:** Failed to connect to the backend at `{FASTAPI_BACKEND_URL}`.\n"
            f"Please ensure the FastAPI server (`main_progress.py`) is running.\n"
            f"Details: {e}"
        )
    except requests.exceptions.RequestException as e:
        progress_bar_placeholder.empty()
        status_text_placeholder.empty()
        result_placeholder.error(
            f"❌ **Request Error:** An error occurred during the request to the backend.\n"
            f"Details: {e}"
        )
    except Exception as e:
        # Catch any other unexpected errors during stream processing
        progress_bar_placeholder.empty()
        status_text_placeholder.empty()
        result_placeholder.error(f"💥 **An unexpected error occurred:**\n{e}")
        st.exception(e) # Show traceback in Streamlit for debugging

else:
    st.info("Click the button above to start the task and see live progress updates.")

st.markdown("---")
st.markdown("*(App will wait for events after connection. If the backend task finishes quickly, you might see the final state directly.)*")
# --- END OF FILE streamlit_app.py ---