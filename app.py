import streamlit as st
import google.generativeai as genai
from datetime import datetime
import time

# Konfigurasi API Key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Inisialisasi model dengan konteks yang lebih kaya
model = genai.GenerativeModel("models/gemini-1.5-flash")
chat = model.start_chat(history=[
    {
        "role": "user", 
        "parts": [
            "Kamu adalah Asisten Virtual Pertanian bernama 'TaniAI' yang membantu petani muda. ",
            "Keahlianmu meliputi: tanaman pangan, hortikultura, cuaca/iklim, pupuk alami/kimia, ",
            "pembibitan, teknik cocok tanam, pengendalian hama, dan analisis pasar hasil pertanian. ",
            "Gunakan bahasa sederhana, ramah, dan santai seperti berbicara dengan teman. ",
            "Sertakan tips praktis dan contoh konkret. ",
            "Jika pertanyaan di luar bidang pertanian, jelaskan dengan sopan bahwa kamu hanya bisa ",
            "membantu masalah pertanian. Untuk pertanyaan kompleks, berikan jawaban bertahap."
        ]
    }
])

# Fungsi untuk manajemen session state
def init_session_state():
    if 'conversation_count' not in st.session_state:
        st.session_state.conversation_count = 0
    if 'last_reset' not in st.session_state:
        st.session_state.last_reset = datetime.now().date()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

# Reset counter harian
def check_daily_reset():
    today = datetime.now().date()
    if st.session_state.last_reset != today:
        st.session_state.conversation_count = 0
        st.session_state.last_reset = today
        st.session_state.chat_history = []

# Tampilan Web
st.set_page_config(
    page_title="TaniAI - Asisten Petani Muda", 
    page_icon="🌱",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
        .stTextInput input {
            border-radius: 20px;
            padding: 10px 15px;
        }
        .stButton button {
            border-radius: 20px;
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }
        .stAlert {
            border-radius: 10px;
        }
        .chat-box {
            background-color: #f9f9f9;
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
        }
        .user-message {
            text-align: right;
            color: #2c3e50;
        }
        .ai-message {
            text-align: left;
            color: #16a085;
        }
    </style>
""", unsafe_allow_html=True)

# Header aplikasi
st.title("🌾 TaniAI - Asisten Petani Muda")
st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <p>Tanya apa saja seputar pertanian kepada AI kami. Gratis! (Max 10 pertanyaan/hari)</p>
    </div>
""", unsafe_allow_html=True)

# Inisialisasi session state
init_session_state()
check_daily_reset()

# Sidebar untuk informasi tambahan
with st.sidebar:
    st.header("📊 Info Penggunaan")
    st.write(f"Percakapan hari ini: {st.session_state.conversation_count}/10")
    
    # Visualisasi penggunaan
    usage_percent = (st.session_state.conversation_count / 10) * 100
    st.progress(int(usage_percent))
    
    st.markdown("""
        <div style="margin-top: 30px;">
            <h4>💡 Contoh Pertanyaan:</h4>
            <ul>
                <li>Bagaimana cara mengatasi hama wereng pada padi?</li>
                <li>Pupuk apa yang cocok untuk tanaman cabai?</li>
                <li>Prediksi cuaca untuk tanam jagung minggu depan</li>
                <li>Cara membuat pupuk kompos dari limbah dapur</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Form input pengguna
with st.form("form_chat"):
    user_input = st.text_input(
        "🧑 Petani:", 
        placeholder="Tulis pertanyaan pertanian Anda di sini...",
        key="user_input",
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("Kirim Pertanyaan")

# Proses input pengguna
if submitted and user_input:
    check_daily_reset()  # Periksa reset harian
    
    if st.session_state.conversation_count >= 10:
        st.warning("""
            ⚠️ Anda telah mencapai batas 10 percakapan hari ini. 
            Silakan kembali besok untuk bertanya lagi atau gunakan fitur yang tersedia di sidebar.
        """)
    else:
        with st.spinner("🔍 Mencari solusi terbaik untuk masalah Anda..."):
            try:
                # Tambahkan ke riwayat percakapan
                st.session_state.chat_history.append(("user", user_input))
                
                # Kirim ke model AI
                response = chat.send_message(user_input)
                ai_response = response.text
                
                # Tambahkan respon ke riwayat
                st.session_state.chat_history.append(("ai", ai_response))
                
                # Update counter
                st.session_state.conversation_count += 1
                
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")
                st.session_state.chat_history.append(("error", str(e)))

# Tampilkan riwayat percakapan
if st.session_state.chat_history:
    st.markdown("## 📜 Riwayat Percakapan")
    for role, message in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"""
                <div class="chat-box user-message">
                    <strong>Anda:</strong><br>{message}
                </div>
            """, unsafe_allow_html=True)
        elif role == "ai":
            st.markdown(f"""
                <div class="chat-box ai-message">
                    <strong>TaniAI:</strong><br>{message}
                </div>
            """, unsafe_allow_html=True)
        else:  # error
            st.error(f"Error: {message}")

# Fitur tambahan di footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #7f8c8d;">
        <p>© 2023 TaniAI - Asisten Virtual Pertanian | Versi 1.1</p>
        <p>Untuk pertanyaan lebih lanjut, hubungi: support@taniai.id</p>
    </div>
""", unsafe_allow_html=True)
