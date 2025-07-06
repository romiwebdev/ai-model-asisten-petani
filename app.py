import streamlit as st
import google.generativeai as genai
from datetime import datetime
import time

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
    "🔍 Periksa daun secara rutin untuk deteksi dini hama penyakit",
    "🌿 Campur tanaman sayuran dengan rempah untuk sistem polyculture",
    "🕊️ Gunakan mulsa jerami untuk menjaga kelembaban tanah",
    "🧂 Gunakan air garam encer untuk mengendalikan gulma di sela paving",
    "🍌 Kulit pisang kaya kalium, bisa dijadikan pupuk cair",
    "☕ Ampas kopi baik untuk tanaman yang suka tanah asam seperti tomat"
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
    },
    {
        "role": "user", 
        "parts": ["Bagaimana menanam cabai rawit di pot?"]
    },
    {
        "role": "model", 
        "parts": ["""Berikut panduan lengkap menanam cabai rawit di pot:

1. **Pilih Pot**: Minimal diameter 30cm dengan lubang drainase
2. **Media Tanam**: Campur tanah, kompos, sekam bakar (2:1:1)
3. **Bibit**: Rendam benih dalam air hangat 2 jam sebelum semai
4. **Penanaman**: Pindahkan bibit setelah punya 4-5 daun sejati
5. **Perawatan**:
   - Siram 1x sehari (jangan sampai tergenang)
   - Beri pupuk NPK 2 minggu sekali
   - Jemur minimal 6 jam/hari
6. **Panen**: Mulai usia 2,5-3 bulan setelah tanam

Tips: Gunakan ajir bambu untuk menyangga tanaman!"""]
    },
    {
        "role": "user",
        "parts": ["Apa game pertanian yang seru?"]
    },
    {
        "role": "model",
        "parts": ["Maaf, saya hanya bisa membahas tentang dunia pertanian nyata. Mungkin Anda ingin tahu tentang permainan edukasi pertanian untuk anak-anak? Atau saya bisa bantu dengan teknik bertanam yang menyenangkan?"]
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
    if 'tips_shown' not in st.session_state:
        st.session_state.tips_shown = False

# Reset counter harian
def check_daily_reset():
    today = datetime.now().date()
    if st.session_state.last_reset != today:
        st.session_state.conversation_count = 0
        st.session_state.last_reset = today
        st.session_state.chat_history = []
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
        .stAlert {
            border-radius: 10px;
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
        .reset-btn {
            background-color: #f44336 !important;
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
check_daily_reset()

# Sidebar untuk informasi tambahan
with st.sidebar:
    # Tips harian
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
                <li>Prediksi cuaca untuk tanam jagung minggu depan</li>
                <li>Cara membuat pupuk kompos dari limbah dapur</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    # Tombol reset percakapan
    if st.button("🔄 Reset Percakapan", key="reset_chat", help="Mulai percakapan baru"):
        st.session_state.chat_history = []
        st.rerun()

# Filter pertanyaan tidak relevan
toxic_keywords = ["game", "film", "musik", "selebriti", "politik", "hiburan", "olahraga"]

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
    
    # Cek pertanyaan tidak relevan
    if any(keyword in user_input.lower() for keyword in toxic_keywords):
        st.warning("Maaf, TaniAI hanya bisa membahas topik pertanian. Silakan ajukan pertanyaan tentang tanaman, pupuk, atau masalah pertanian lainnya.")
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("ai", "Saya hanya bisa membantu dengan masalah pertanian. Ada yang bisa saya bantu seputar bercocok tanam?"))
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
        <p>Dikembangkan oleh Romi | <a href="https://romifullstack.vercel.app" target="_blank">romifullstack.vercel.app</a></p>
    </div>
""", unsafe_allow_html=True)
