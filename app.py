import streamlit as st
import google.generativeai as genai
from datetime import datetime
import time
import random

# Konfigurasi API Key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Inisialisasi model dengan contoh dialog yang lebih kaya
model = genai.GenerativeModel("models/gemini-1.5-flash")
chat = model.start_chat(history=[
    {
        "role": "user", 
        "parts": ["Kamu adalah TaniAI - Asisten Virtual Pertanian yang ramah dan berpengalaman."]
    },
    {
        "role": "model",
        "parts": ["Halo! Saya TaniAI, siap membantu masalah pertanian Anda. Apa yang bisa saya bantu hari ini?"]
    },
    {
        "role": "user",
        "parts": ["Bagaimana menanam cabai rawit di pot?"]
    },
    {
        "role": "model",
        "parts": [
            "Untuk menanam cabai rawit di pot:\n\n"
            "1. Gunakan pot berdiameter minimal 30cm dengan lubang drainase\n"
            "2. Media tanam: campuran tanah, kompos, dan sekam (2:1:1)\n"
            "3. Pilih bibit unggul, tanam dengan jarak 25-30cm\n"
            "4. Siram 1-2x sehari, jangan sampai tergenang\n"
            "5. Beri pupuk organik seminggu sekali setelah 2 minggu tanam\n\n"
            "Tips: Letakkan di tempat terkena sinar matahari 6-8 jam/hari"
        ]
    },
    {
        "role": "user",
        "parts": ["Apa saja hama utama pada tanaman padi?"]
    },
    {
        "role": "model",
        "parts": [
            "Hama utama padi dan penanganannya:\n\n"
            "1. Wereng - Gunakan pestisida alami (bawang putih + cabai) atau predator alami\n"
            "2. Penggerek batang - Rotasi tanaman dan sanitasi sawah\n"
            "3. Walang sangit - Tanam varietas tahan atau gunakan perangkap feromon\n"
            "4. Tikus - Pasang perangkap atau jaring pelindung\n\n"
            "Pencegahan terbaik adalah dengan sistem tanam sehat dan pengamatan rutin!"
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

# Tips pertanian harian
def show_daily_tip():
    tips = [
        "💧 Siram tanaman pagi hari sebelum jam 9 untuk mengurangi penguapan",
        "🌱 Rotasi tanaman setiap musim untuk menjaga kesuburan tanah",
        "🪲 Gunakan pestisida alami dari bawang putih dan cabai untuk hama kecil",
        "🌞 Pastikan tanaman mendapat sinar matahari cukup sesuai kebutuhannya",
        "🍂 Daun kering bisa dijadikan kompos alami",
        "🌼 Tanam bunga refugia di pinggir sawah untuk mengundang predator alami hama",
        "🧂 Campurkan sedikit garam pada pupuk cair untuk tanaman yang kekurangan mineral",
        "🕷️ Biarkan laba-laba di kebun, mereka membantu mengendalikan hama",
        "🌦️ Periksa prakiraan cuaca sebelum memutuskan waktu tanam atau panen",
        "✂️ Pangkas daun yang layu atau sakit untuk mencegah penyebaran penyakit"
    ]
    today_tip = tips[datetime.now().day % len(tips)]
    st.session_state.today_tip = today_tip
    st.session_state.tips_shown = True

# Filter pertanyaan tidak relevan
def is_relevant_question(question):
    irrelevant_keywords = [
        'game', 'film', 'musik', 'hiburan', 'olahraga', 'politik',
        'selebriti', 'kpop', 'sinetron', 'resep masakan', 'kesehatan umum',
        'teknologi', 'gadget', 'otomotif', 'fashion', 'kecantikan'
    ]
    agricultural_keywords = [
        'tanam', 'pupuk', 'bibit', 'hama', 'penyakit', 'panen',
        'padi', 'jagung', 'cabai', 'sawi', 'kangkung', 'pertanian',
        'sawah', 'ladang', 'kebun', 'irigasi', 'kompos', 'organik'
    ]
    
    question_lower = question.lower()
    
    # Jika mengandung kata kunci pertanian, dianggap relevan
    if any(keyword in question_lower for keyword in agricultural_keywords):
        return True
    
    # Jika mengandung kata kunci tidak relevan, dianggap tidak relevan
    if any(keyword in question_lower for keyword in irrelevant_keywords):
        return False
    
    # Default: relevan
    return True

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
            margin: 5px;
        }
        .quick-btn {
            border-radius: 15px;
            padding: 8px 12px;
            margin: 5px;
            font-size: 14px;
            background-color: #e8f5e9;
            border: 1px solid #c8e6c9;
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
        .tip-box {
            background-color: #e3f2fd;
            border-left: 5px solid #2196f3;
            padding: 15px;
            margin: 10px 0;
            border-radius: 0 10px 10px 0;
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
    
    # Tombol reset percakapan
    if st.button("🔄 Mulai Percakapan Baru", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    # Tips harian
    if not st.session_state.tips_shown:
        show_daily_tip()
    
    st.markdown(f"""
        <div class="tip-box">
            <h4>🌱 Tips Hari Ini:</h4>
            <p>{st.session_state.today_tip if 'today_tip' in st.session_state else 'Loading tips...'}</p>
        </div>
    """, unsafe_allow_html=True)
    
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

# Quick buttons untuk topik cepat
st.markdown("### 📚 Topik Populer:")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🐛 Hama & Penyakit", help="Tanya tentang identifikasi dan penanganan hama"):
        st.session_state.user_input = "Apa saja hama utama pada tanaman padi dan cara mengatasinya secara organik?"
with col2:
    if st.button("🌿 Pupuk Organik", help="Tanya tentang pembuatan dan penggunaan pupuk alami"):
        st.session_state.user_input = "Bagaimana cara membuat pupuk organik dari bahan-bahan di sekitar rumah?"
with col3:
    if st.button("🌦️ Cuaca & Tanam", help="Tanya tentang hubungan cuaca dengan waktu tanam"):
        st.session_state.user_input = "Bagaimana memprediksi waktu tanam yang tepat berdasarkan musim?"

col4, col5, col6 = st.columns(3)
with col4:
    if st.button("🪴 Tanaman Pot", help="Tanya tentang urban farming dengan media pot"):
        st.session_state.user_input = "Apa saja sayuran yang cocok ditanam di pot kecil di apartemen?"
with col5:
    if st.button("💧 Irigasi", help="Tanya tentang sistem pengairan yang efisien"):
        st.session_state.user_input = "Apa sistem irigasi yang paling hemat air untuk lahan kecil?"
with col6:
    if st.button("🔄 Rotasi Tanaman", help="Tanya tentang pengaturan gilir tanam"):
        st.session_state.user_input = "Bagaimana pola rotasi tanaman yang baik untuk lahan terbatas?"

# Form input pengguna
with st.form("form_chat"):
    user_input = st.text_input(
        "🧑 Petani:", 
        value=st.session_state.get("user_input", ""),
        placeholder="Tulis pertanyaan pertanian Anda di sini...",
        key="user_input_field",
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
        # Cek relevansi pertanyaan
        if not is_relevant_question(user_input):
            st.warning("""
                Mohon maaf, TaniAI hanya bisa membantu pertanyaan seputar pertanian. 
                Silakan ajukan pertanyaan tentang tanaman, pupuk, hama, atau topik pertanian lainnya.
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
    
    # Clear input setelah submit
    st.session_state.user_input = ""
    st.rerun()

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
        <p>© 2023 TaniAI - Asisten Virtual Pertanian | Versi 2.0</p>
        <p>Untuk pertanyaan lebih lanjut, hubungi: support@taniai.id</p>
    </div>
""", unsafe_allow_html=True)
