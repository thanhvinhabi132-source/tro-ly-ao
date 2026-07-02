import streamlit as st
from datetime import date, datetime
from gtts import gTTS
import base64
import io
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from pydub import AudioSegment

# --- 1. CẤU HÌNH GIAO DIỆN & STYLE CSS NÂNG CAO ---
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
    
    .mic-box {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
    }
    div[data-testid="stMarkdownContainer"] + div button {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%) !important;
        color: white !important;
        border: none !important;
        width: 90px !important;
        height: 90px !important;
        border-radius: 50% !important;
        font-weight: bold !important;
        font-size: 24px !important;
        box-shadow: 0 0 20px rgba(255, 75, 43, 0.6) !important;
        transition: all 0.3s ease-in-out !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[data-testid="stMarkdownContainer"] + div button:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 0 30px rgba(255, 75, 43, 0.9) !important;
        background: linear-gradient(135deg, #FF4B2B 0%, #FF416C 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="title-gradient">ABI VIRTUAL ASSISTANT</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Trợ lý ảo phiên bản Web Cloud (Hỗ trợ Giọng nói)</p>', unsafe_allow_html=True)

# --- 2. KHỞI TẠO BỘ NHỚ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Click the glowing Microphone button below to talk to me!"}
    ]
if "audio_to_play" not in st.session_state:
    st.session_state.audio_to_play = None

# --- 3. CÁC HÀM XỬ LÝ LÕI ---
def get_suffix(d):
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")

def get_robot_speak_b64(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return base64.b64encode(fp.read()).decode()
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

# --- 5. BỐ CỤC ĐIỀU KHIỂN & MICROPHONE ---
st.write("---")
st.markdown('<div class="mic-box">', unsafe_allow_html=True)

# Ghi âm mic từ trình duyệt với key='my_mic'
audio_recorded = mic_recorder(
    start_prompt="🎙️",
    stop_prompt="🛑",
    key='my_mic'
)

st.markdown('</div>', unsafe_allow_html=True)

user_query = st.chat_input("Hoặc nhập tin nhắn bằng chữ ở đây...")
final_user_text = None

if user_query:
    final_user_text = user_query

if audio_recorded and 'bytes' in audio_recorded:
    audio_bytes = audio_recorded['bytes']
    
    try:
        sound = AudioSegment.from_file(io.BytesIO(audio_bytes))
        wav_fp = io.BytesIO()
        sound.export(wav_fp, format="wav")
        wav_fp.seek(0)
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_fp) as source:
            audio_data = recognizer.record(source)
            text_converted = recognizer.recognize_google(audio_data, language="en-US")
            final_user_text = text_converted
    except sr.UnknownValueError:
        st.toast("Robot không nghe rõ, bạn nói lại nhé!", icon="🤔")
    except Exception as e:
        st.toast(f"Lỗi xử lý âm thanh: {e}", icon="⚠️")
        
    # LÝ DO FIX: Xóa sạch dữ liệu trong session_state của mic để tránh lặp lại khi rerun
    if 'my_mic' in st.session_state:
        st.session_state['my_mic'] = None

# --- 6. XỬ LÝ PHẢN HỒI ---
if final_user_text:
    st.session_state.messages.append({"role": "user", "content": final_user_text})
    response_text = process_brain(final_user_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    audio_b64 = get_robot_speak_b64(response_text)
    if audio_b64:
        st.session_state.audio_to_play = audio_b64
        
    st.rerun()

if st.session_state.audio_to_play:
    audio_html = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{st.session_state.audio_to_play}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    st.session_state.audio_to_play =
