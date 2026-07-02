import streamlit as st
from datetime import date, datetime
from gtts import gTTS
import base64
import io
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder

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
    
    /* Làm đẹp khu vực nút bấm Microphone của thư viện */
    .mic-container {
        display: flex;
        justify-content: center;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="title-gradient">ABI VIRTUAL ASSISTANT</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Trợ lý ảo phiên bản Web Cloud (Hỗ trợ Giọng nói)</p>', unsafe_allow_html=True)

# --- 2. KHỞI TẠO BỘ NHỚ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your web assistant. Click '🎙️ Start Recording' to talk or type below!"}
    ]
if "audio_to_play" not in st.session_state:
    st.session_state.audio_to_play = None

# --- 3. CÁC HÀM XỬ LÝ LÕI ---
def get_suffix(d):
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")

def get_robot_speak_b64(text):
    """Chuyển phản hồi văn bản thành âm thanh Base64 để trình duyệt tự phát"""
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

# --- 5. BỐ CỤC ĐIỀU KHIỂN & MICROPHONE TRÊN WEB ---
st.write("---")
st.markdown('<div class="mic-container">', unsafe_allow_html=True)

# Nút bấm ghi âm từ trình duyệt web công khai
audio_recorded = mic_recorder(
    start_prompt="🎙️ Bắt đầu nói (Start)",
    stop_prompt="🛑 Dừng & Gửi (Stop)",
    key='mic'
)

st.markdown('</div>', unsafe_allow_html=True)

# Ô nhập chữ thông thường phòng khi không muốn nói
user_query = st.chat_input("Hoặc nhập tin nhắn bằng chữ ở đây...")

# Biến trung gian chứa văn bản người dùng (từ gõ chữ hoặc nói)
final_user_text = None

# Trường hợp 1: Nếu người dùng GÕ CHỮ
if user_query:
    final_user_text = user_query

# Trường hợp 2: Nếu người dùng BẤM NÓI và có dữ liệu âm thanh truyền về
if audio_recorded and 'bytes' in audio_recorded:
    audio_bytes = audio_recorded['bytes']
    
    # Chuyển đổi dữ liệu âm thanh dạng bytes sang định dạng file mà SpeechRecognition hiểu được
    recognizer = sr.Recognizer()
    audio_file = io.BytesIO(audio_bytes)
    
    with sr.AudioFile(audio_file) as source:
        try:
            # Đọc dữ liệu âm thanh và nhận diện giọng nói bằng Google API công khai
            audio_data = recognizer.record(source)
            text_converted = recognizer.recognize_google(audio_data, language="en-US")
            final_user_text = text_converted
        except sr.UnknownValueError:
            st.toast("Robot không hiểu âm thanh này, hãy thử nói lại rõ hơn!", icon="🤔")
        except Exception as e:
            st.toast(f"Lỗi nhận diện: {e}", icon="⚠️")

# --- 6. XỬ LÝ PHẢN HỒI CHUNG ---
if final_user_text:
    # Lưu câu hỏi của User vào lịch sử và hiển thị
    st.session_state.messages.append({"role": "user", "content": final_user_text})
    
    # AI xử lý câu trả lời
    response_text = process_brain(final_user_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # Tạo âm thanh robot trả lời
    audio_b64 = get_robot_speak_b64(response_text)
    if audio_b64:
        st.session_state.audio_to_play = audio_b64
        
    st.rerun()

# Phát âm thanh tự động (nếu có dữ liệu mới)
if st.session_state.audio_to_play:
    audio_html = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{st.session_state.audio_to_play}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    st.session_state.audio_to_play = None  # Xóa trạng thái phát sau khi chèn HTML để tránh lặp lại
