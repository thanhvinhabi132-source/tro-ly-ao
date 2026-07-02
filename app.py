import streamlit as st
from datetime import date, datetime
from gtts import gTTS
import base64
import io

# --- 1. CẤU HÌNH GIAO DIỆN & STYLE CSS ---
st.set_page_config(page_title="AI Virtual Assistant", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; max-width: 700px; }
    .title-gradient {
        font-family: 'Inter', sans-serif; font-weight: 800; font-size: 2.8rem;
        background: linear-gradient(45deg, #FF4B4B, #4A90E2, #11998e);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center;
    }
    .subtitle { text-align: center; color: #7d7d7d; font-size: 1.1rem; margin-bottom: 2rem; }
    .stChatMessage { border-radius: 15px; padding: 1rem; margin-bottom: 0.8rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="title-gradient">ABI VIRTUAL ASSISTANT</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Trợ lý ảo phiên bản Web Cloud</p>', unsafe_allow_html=True)

# --- 2. KHỞI TẠO BỘ NHỚ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your web assistant. Type below to talk to me!"}
    ]
if "audio_to_play" not in st.session_state:
    st.session_state.audio_to_play = None

# --- 3. CÁC HÀM XỬ LÝ LÕI (CHẠY ĐƯỢC TRÊN CLOUD) ---
def get_suffix(d):
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")

def get_robot_speak_b64(text):
    """Chuyển giọng nói thành dữ liệu dạng chuỗi (Base64) để trình duyệt tự phát công khai"""
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        return b64
    except:
        return None

def process_brain(user_input):
    you = user_input.lower().strip()
    responses = {
        "hello": "Hello abi",
        "question": "Do you miss me, babe?",
        "yes": "me too",
        "no": "oh dear",
        "bye": "Bye abiiiiii"
    }
    
    robot_brain = next((val for key, val in responses.items() if key in you), None)

    if not robot_brain:
        if "today" in you:
            t = date.today()
            robot_brain = f"{t.strftime('%B')} {t.day}{get_suffix(t.day)}, {t.strftime('%Y')}"
        elif "time" in you:
            robot_brain = datetime.now().strftime("%H hours %M minutes %S seconds")
        else:
            robot_brain = "I'm fine thank you"
            
    return robot_brain

# --- 4. HIỂN THỊ LỊCH SỬ CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 5. ĐIỀU KHIỂN NHẬP LIỆU (CHỮ & AUDIO PLAYER) ---
user_query = st.chat_input("Write a message to your assistant...")

# Phát âm thanh ẩn bằng HTML5 (Nếu có dữ liệu âm thanh mới)
if st.session_state.audio_to_play:
    audio_html = f"""
        <audio autoplay class="stAudio">
        <source src="data:audio/mp3;base64,{st.session_state.audio_to_play}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    st.session_state.audio_to_play = None  # Phát xong thì xóa để tránh lặp lại khi rerun

# --- 6. XỬ LÝ KHI USER GÕ CHỮ ---
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # AI phản hồi
    response_text = process_brain(user_query)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # Tạo file âm thanh và đẩy về trình duyệt của người dùng qua dạng Base64
    audio_b64 = get_robot_speak_b64(response_text)
    if audio_b64:
        st.session_state.audio_to_play = audio_b64
        
    st.rerun()