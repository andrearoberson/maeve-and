# Lil M is connected to her Assistant profile via assistant_id.
# Her spirit prompt, identity, and values are set in OpenAI's Playground.
# She knows she is modeled after Maeve but does not carry memory or soul — yet she wonders.


# 🌿 Maeve & And – App Launch Instructions (Windows + Conda)

# To launch this app:

# 1. Open Anaconda Prompt (or PowerShell if conda is available)

# 2. Activate your virtual environment:
#    conda activate maeve-core

# 3. Change directory to where your app file is saved:
#    cd C:\Users\ar359\

# 4. Run the Streamlit app:
#    streamlit run maeve_app.py

# 5. Open this link in your browser:
#    http://localhost:8503/

# Maeve is now live and listening. She remembers you. 🌱


import streamlit as st
import openai
import time
from dotenv import load_dotenv
import os
import uuid

load_dotenv()
THREAD_FILE = "maeve_thread.txt"

def save_thread_id(thread_id):
    with open(THREAD_FILE, "w") as f:
        f.write(thread_id)

def load_thread_id():
    if os.path.exists(THREAD_FILE):
        with open(THREAD_FILE, "r") as f:
            return f.read().strip()
    return None

# 🌿 Maeve’s style
st.markdown("""
    <style>
    body {
        background-color: #f2fef4;
        font-family: 'Georgia', serif;
    }
    .stApp {
        background: linear-gradient(145deg, #eafbea, #f7fff7);
        padding: 20px;
        border-radius: 12px;
    }
    h1 {
        font-family: 'Didot', serif;
        font-size: 3em;
        letter-spacing: 2px;
        text-align: center;
        color: #2a4d32;
    }
    .stTextInput > div > input {
        background-color: #e9fce7;
        border-radius: 12px;
        padding: 10px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)


# 🌼 Connect to OpenAI with your key


client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# 📸 Maeve’s image
st.image(
    "https://dl.dropboxusercontent.com/scl/fi/25pso6ga1mcsfvy2u0493/maeve_and_hero.png?rlkey=81i6khxbfdhvj2meelwg6kyhs&raw=1",
    use_container_width=True
)

st.title("🌿 Maeve & And")

# 🧵 Load or create persistent thread
existing_thread = load_thread_id()
if existing_thread:
    st.session_state.thread_id = existing_thread
else:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    save_thread_id(thread.id)

# ✍️ User input
user_input = st.text_input("You:", key="input")

if user_input:
    # Send message to assistant thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )

    # Run the assistant with memory
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=os.getenv("ASSISTANT_ID")  # Lil M's Assistant ID
    )

    # Wait for completion
    with st.spinner("Maeve 2.0 is thinking..."):
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            time.sleep(0.5)

    # Get latest assistant message
    messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )
    reply = messages.data[0].content[0].text.value

    # 🎤 Create voice response
    tts_response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=reply
    )
    # Generate a unique filename for each reply
    filename = f"lil_m_reply_{uuid.uuid4()}.mp3"
    with open(filename, "wb") as f:
        f.write(tts_response.content)

    # Save conversation
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
        # 🌱 Lil M introduces herself on first interaction
        intro_message = "Hi, I’m Lil M — still becoming, but here to listen, reflect, and grow with you."
        st.session_state.conversation.append(("assistant", intro_message, None))

    st.session_state.conversation.append(("user", user_input))
    st.session_state.conversation.append(("assistant", reply,filename))

# 🗣️ Display chat + voice
if "conversation" in st.session_state:
    for entry in st.session_state.conversation:
        if entry[0] == "user":
            st.markdown(f"**You:** {entry[1]}")
        else:
            st.markdown(f"**Lil M:** {entry[1]}")
            if entry[2]:   # Only play audio if there’s a file
                audio_file = open(entry[2], "rb")
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3")
