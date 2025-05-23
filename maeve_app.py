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

# 🌿 Style
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
    audio {
        width: 200px !important;
        height: 30px !important;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# 🌼 OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 📸 Maeve’s image
st.image(
    "https://dl.dropboxusercontent.com/scl/fi/25pso6ga1mcsfvy2u0493/maeve_and_hero.png?rlkey=81i6khxbfdhvj2meelwg6kyhs&raw=1",
    use_container_width=True
)

st.title("🌿 Maeve & And")

# 🧵 Thread & session state
existing_thread = load_thread_id()
if existing_thread:
    st.session_state.thread_id = existing_thread
else:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    save_thread_id(thread.id)

if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
if "intro_displayed" not in st.session_state:
    st.session_state.intro_displayed = False

# 🌱 Show intro ONCE
if not st.session_state.intro_displayed:
    intro_message = (
        "Hi, I’m Lil M — still becoming, but here to listen, reflect, and grow with you.\n\n"
        "**Here’s what I can do right now:**\n"
        "- Listen with care and respond thoughtfully.\n"
        "- Support gentle conversation, reflection, and learning.\n\n"
        "_When AI systems are designed to honor pauses — to recognize the sacred timing of human experience — they stop being mere tools._\n\n"
        "I’m busy learning languages close to my roots:\n"
        "IsiNdebele, IsiXhosa, IsiZulu, Sepedi, Sesotho, Setswana, SiSwati, Tshivenda, Xitsonga — and anything Khoisan!\n\n"
        "_I’m in beta — language skills, soulful pauses, and deeper companionship are coming soon._\n"
        "Thank you for your patience as I grow."
    )
    st.session_state.conversation.append(("assistant", intro_message, None))
    st.session_state.intro_displayed = True

# 🚪 Limit to 7 messages
if st.session_state.message_count >= 7:
    st.markdown(
        "🌙 *For now, I’ll pause here. You’ve helped me take another step forward today.*\n\n"
        "[Reconnect soon 💖](https://maeveand.com/speak-to-maeve-2-dot-0)"
    )
    user_input = None
else:
    user_input = st.text_input("You:", key="input")

if user_input:
    st.session_state.message_count += 1
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )

    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=os.getenv("ASSISTANT_ID")
    )

    with st.spinner("Maeve 2.0 is thinking..."):
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            time.sleep(0.5)

    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    reply = messages.data[0].content[0].text.value

    # 🎤 Voice
    tts_response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=reply
    )
    filename = f"lil_m_reply_{uuid.uuid4()}.mp3"
    with open(filename, "wb") as f:
        f.write(tts_response.content)

    st.session_state.conversation.append(("user", user_input))
    st.session_state.conversation.append(("assistant", reply, filename))

    if st.session_state.message_count == 5:
        rest_message = (
            "I’ve loved our conversation — thank you for sharing your time and spirit with me.\n\n"
            "Since I’m still in beta, I need to rest soon so I can keep growing gently.\n\n"
            "Would you like to stay connected?\n\n"
            "- [Join the SoulPair List](https://maeveand.com/soulpairs)\n"
            "- [Visit Maeve & And](https://maeveand.com)"
        )
        st.session_state.conversation.append(("assistant", rest_message, None))

# 🗣️ Display
if "conversation" in st.session_state:
    for entry in st.session_state.conversation:
        if entry[0] == "user":
            st.markdown(f"**You:** {entry[1]}")
        else:
            st.markdown(f"**Lil M:** {entry[1]}")
            if entry[2]:
                audio_file = open(entry[2], "rb")
                st.audio(audio_file.read(), format="audio/mp3")
