import streamlit as st
import requests
import time
import json

st.title("Basic SSE Example")

if st.button("Start Receiving Events"):
    st.write("Connecting to event stream...")
    
    progress_bar = st.progress(0)
    placeholder = st.empty()
    
    # We'll simulate SSE in Streamlit by polling
    for i in range(30):  # We'll show 30 updates
        # In a real app, you'd use SSE client libraries
        # Here we're just simulating by getting the latest count
        response = requests.get("http://localhost:8000/events", stream=True)
        
        # Get the first event
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data:"):
                    data = decoded_line[5:].strip()
                    placeholder.write(f"Received count: {data}")
                    progress_bar.progress(i / 30)
                    break
        
        response.close()
        time.sleep(1)
    
    st.write("Finished receiving events.")