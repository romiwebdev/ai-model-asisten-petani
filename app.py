import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Konfigurasi API Key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Daftar tips harian
tips_pertanian = [
    "💧 Siram tanaman pagi atau sore untuk mengurangi penguapan air",
    "♻️ Buat kompos dari limbah dapur untuk pupuk alami",
    "🔄 Lakukan rotasi tanaman untuk menjaga kesuburan tanah",
    "🌱 Gunakan pot dengan lubang drainase untuk hindari busuk akar",
    "🐞 Tanam bunga marigold di sekitar kebun untuk mengusir hama",
    "🌞 Kenali kebutuhan sinar matahari tiap tanaman (full sun/partial shade)",
    "📅 Buat jadwal rutin pemupukan setiap 2-4 minggu sekali",
    "✂️ Pangkas daun/tunas yang layu untuk stimulasi pertumbuhan baru",
    "🌧️ Manfaatkan air hujan dengan membuat penampungan sederhana",
    "🔍 Periksa daun secara rutin untuk deteksi dini hama penyakit"
]

# Inisialisasi model dengan contoh percakapan
model = genai.GenerativeModel("models/gemini-1.5-flash")
chat = model.start_chat(history=[
    {
        "role": "user",
        "parts": ["Kamu siapa dan bisa bantu apa?"]
    },
    {
        "role": "model",
        "parts": ["""Halo! Saya TaniAI, asisten virtual pertanian. Saya bisa membantu Anda dengan:
- Masalah tanam-menanam (cabai, tomat, padi, dll)
- Rekomendasi pupuk & pengendalian hama
- Analisis kondisi tanah & cuaca
- Teknik berkebun di lahan sempit
- Pengolahan hasil panen

Ada yang bisa saya bantu hari ini?"""]
    }
])

# Fungsi untuk session state
def init_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'tips_shown' not in st.session_state:
        st.session_state.tips_shown = False

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
            padding: 10px 20px;
        }
        .chat-box {
            background-color: #f9f9f9;
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .user-message {
            text-align: right;
            color: #2c3e50;
            margin-left: 20%;
        }
        .ai-message {
            text-align: left;
            color: #16a085;
            margin-right: 20%;
        }
    </style>
""", unsafe_allow_html=True)

# Header aplikasi
st.title("🌾 TaniAI - Asisten Petani Muda")
st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <p>Tanya apa saja seputar pertanian kepada AI kami</p>
    </div>
""", unsafe_allow_html=True)

# Inisialisasi session state
init_session_state()

# Sidebar untuk tips harian
with st.sidebar:
    if not st.session_state.tips_shown:
        today_tip = tips_pertanian[datetime.now().day % len(tips_pertanian)]
        st.info(f"🌱 Tips Hari Ini:\n\n{today_tip}")
        st.session_state.tips_shown = True
    
    st.markdown("""
        <div style="margin-top: 30px;">
            <h4>💡 Contoh Pertanyaan:</h4>
            <ul>
                <li>Bagaimana mengatasi hama wereng pada padi?</li>
                <li>Pupuk apa yang cocok untuk tanaman cabai?</li>
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
    with st.spinner("🔍 Mencari solusi terbaik untuk masalah Anda..."):
        try:
            # Tambahkan ke riwayat percakapan
            st.session_state.chat_history.append(("user", user_input))
            
            # Kirim ke model AI
            response = chat.send_message(user_input)
            ai_response = response.text
            
            # Tambahkan respon ke riwayat
            st.session_state.chat_history.append(("ai", ai_response))
            
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

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #7f8c8d;">
        <p>© 2025 TaniAI | Dikembangkan oleh <a href="https://romifullstack.vercel.app" target="_blank">Romi</a></p>
    </div>
""", unsafe_allow_html=True)
