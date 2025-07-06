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
        "parts": ["Kamu adalah TaniAI - Asisten Virtual Pertanian profesional."]
    },
    {
        "role": "model",
        "parts": ["Halo! Saya TaniAI, siap membantu masalah pertanian Anda dengan solusi praktis."]
    }
])

# ========== FUNGSI UTILITAS ==========
def init_session_state():
    if 'conversation_count' not in st.session_state:
        st.session_state.conversation_count = 0
    if 'last_reset' not in st.session_state:
        st.session_state.last_reset = datetime.now().date()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'tips_shown' not in st.session_state:
        st.session_state.tips_shown = False

def check_daily_reset():
    today = datetime.now().date()
    if st.session_state.last_reset != today:
        st.session_state.conversation_count = 0
        st.session_state.last_reset = today
        st.session_state.chat_history = []
        st.session_state.tips_shown = False

def show_daily_tip():
    tips = [
        "💧 Siram pagi hari sebelum jam 9 untuk efisiensi air",
        "🌱 Rotasi tanaman setiap musim untuk menjaga kesuburan tanah",
        "🪲 Gunakan pestisida alami dari bawang putih + cabai",
        "🌞 Sesuaikan jarak tanam dengan kebutuhan sinar matahari",
        "🍂 Daun kering bisa jadi kompos alami",
        "🌼 Tanam bunga refugia untuk undang predator alami hama",
        "🧂 Tambahkan sedikit garam pada pupuk cair untuk tanaman kurang mineral",
        "🕷️ Biarkan laba-laba di kebun - mereka pengendali hama alami",
        "🌦️ Periksa prakiraan cuaca sebelum tanam/panen",
        "✂️ Pangkas daun layu untuk cegah penyebaran penyakit"
    ]
    st.session_state.today_tip = random.choice(tips)
    st.session_state.tips_shown = True

def is_relevant_question(question):
    irrelevant_keywords = ['game', 'film', 'musik', 'hiburan', 'politik']
    agricultural_keywords = ['tanam', 'pupuk', 'bibit', 'hama', 'panen', 'pertanian']
    return any(kw in question.lower() for kw in agricultural_keywords)

# ========== TAMPILAN UI ==========
st.set_page_config(
    page_title="TaniAI Pro - Asisten Petani Modern",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom
st.markdown(f"""
    <style>
        /* Font dan Warna Dasar */
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, #2e7d32, #388e3c);
            color: white;
            padding: 2rem;
            border-radius: 0 0 15px 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        
        /* Tombol Utama */
        .stButton>button {{
            border-radius: 25px;
            background: linear-gradient(135deg, #388e3c, #2e7d32);
            color: white;
            font-weight: 600;
            padding: 0.5rem 1.5rem;
            border: none;
            transition: all 0.3s;
        }}
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        /* Tombol Topik Cepat */
        .quick-btn {{
            border-radius: 20px;
            padding: 0.7rem 1rem;
            margin: 0.3rem;
            font-size: 0.9rem;
            background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
            border: none;
            color: #1b5e20;
            font-weight: 500;
            transition: all 0.2s;
            width: 100%;
            text-align: center;
        }}
        .quick-btn:hover {{
            background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
            transform: translateY(-2px);
        }}
        
        /* Chat Box */
        .chat-box {{
            border-radius: 18px;
            padding: 1.2rem 1.5rem;
            margin: 0.8rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            max-width: 85%;
            word-wrap: break-word;
        }}
        .user-message {{
            background-color: #e3f2fd;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }}
        .ai-message {{
            background-color: #f1f8e9;
            margin-right: auto;
            border-bottom-left-radius: 5px;
        }}
        
        /* Sidebar */
        .sidebar .sidebar-content {{
            background-color: #f5f5f6;
            padding: 1.5rem;
        }}
        .usage-card {{
            background: white;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }}
        
        /* Responsif */
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.8rem; }}
            .quick-btn {{ font-size: 0.8rem; padding: 0.6rem; }}
            .chat-box {{ max-width: 95%; }}
        }}
    </style>
""", unsafe_allow_html=True)

# ========== HEADER ==========
st.markdown("""
    <div class="header">
        <div style="display: flex; align-items: center; gap: 15px;">
            <h1 style="margin: 0; font-weight: 700;">🌱 TaniAI Pro</h1>
            <div style="background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 20px; font-size: 0.9rem;">
                Asisten Pertanian Modern
            </div>
        </div>
        <p style="margin: 0.5rem 0 0; opacity: 0.9;">Dapatkan solusi cerdas untuk masalah pertanian Anda</p>
    </div>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h3 style="color: #2e7d32; border-bottom: 2px solid #81c784; padding-bottom: 0.5rem;">Dashboard</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Kartu Penggunaan
    st.markdown("""
        <div class="usage-card">
            <h4 style="margin-top: 0; color: #388e3c;">📊 Penggunaan Harian</h4>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>Percakapan:</span>
                <span style="font-weight: 600;">{}/10</span>
            </div>
            <div style="height: 10px; background: #e0e0e0; border-radius: 5px; margin-bottom: 1rem;">
                <div style="height: 100%; width: {}%; background: linear-gradient(90deg, #81c784, #4caf50); border-radius: 5px;"></div>
            </div>
            <button onclick="window.location.reload()" style="width: 100%; background: #f5f5f5; border: 1px solid #e0e0e0; border-radius: 8px; padding: 8px; cursor: pointer; transition: all 0.3s;">
                🔄 Reset Percakapan
            </button>
        </div>
    """.format(
        st.session_state.get('conversation_count', 0),
        (st.session_state.get('conversation_count', 0) / 10) * 100
    ), unsafe_allow_html=True)
    
    # Tips Harian
    if not st.session_state.tips_shown:
        show_daily_tip()
    
    st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 1.5rem;">
            <h4 style="margin-top: 0; color: #388e3c;">🌿 Tips Hari Ini</h4>
            <div style="background: #e8f5e9; padding: 0.8rem; border-radius: 8px; border-left: 4px solid #4caf50;">
                {st.session_state.today_tip if 'today_tip' in st.session_state else 'Memuat tips...'}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Contoh Pertanyaan
    st.markdown("""
        <div style="background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <h4 style="margin-top: 0; color: #388e3c;">💡 Contoh Pertanyaan</h4>
            <ul style="padding-left: 1.2rem; margin-bottom: 0;">
                <li style="margin-bottom: 0.5rem;">Bagaimana mengatasi hama wereng?</li>
                <li style="margin-bottom: 0.5rem;">Pupuk terbaik untuk cabai?</li>
                <li style="margin-bottom: 0.5rem;">Cara membuat kompos cepat</li>
                <li>Teknik tanam hidroponik sederhana</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# ========== KONTEN UTAMA ==========
init_session_state()
check_daily_reset()

# Section Topik Cepat
st.markdown("""
    <div style="margin: 1.5rem 0;">
        <h3 style="color: #2e7d32; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.2em;">🧭</span> Topik Cepat
        </h3>
        <p style="margin-top: -0.5rem; color: #666; font-size: 0.95rem;">Pilih topik untuk memulai percakapan</p>
    </div>
""", unsafe_allow_html=True)

# Grid Tombol Topik Cepat
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🐛 Hama & Penyakit", key="hama_btn", help="Identifikasi dan atasi masalah hama"):
        st.session_state.user_input = "Bagaimana mengidentifikasi dan mengatasi hama wereng pada padi secara organik?"
with col2:
    if st.button("🌿 Pupuk Organik", key="pupuk_btn", help="Pembuatan dan penggunaan pupuk alami"):
        st.session_state.user_input = "Apa saja bahan rumah tangga yang bisa dijadikan pupuk organik dan cara pembuatannya?"
with col3:
    if st.button("🌦️ Cuaca & Tanam", key="cuaca_btn", help="Panduan tanam berdasarkan musim"):
        st.session_state.user_input = "Bagaimana memprediksi waktu tanam yang ideal berdasarkan pola cuaca saat ini?"

col4, col5, col6 = st.columns(3)
with col4:
    if st.button("🪴 Urban Farming", key="urban_btn", help="Pertanian di lahan terbatas"):
        st.session_state.user_input = "Teknik urban farming apa yang efektif untuk pemula di apartemen?"
with col5:
    if st.button("💧 Irigasi Pintar", key="irigasi_btn", help="Sistem pengairan efisien"):
        st.session_state.user_input = "Sistem irigasi apa yang paling hemat air untuk kebun kecil?"
with col6:
    if st.button("🔄 Rotasi Tanaman", key="rotasi_btn", help="Pengaturan gilir tanam"):
        st.session_state.user_input = "Bagaimana pola rotasi tanaman yang baik untuk lahan terbatas?"

# Form Input Pengguna
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Tanyakan masalah pertanian Anda:",
        value=st.session_state.get("user_input", ""),
        placeholder="Contoh: Cara mengatasi daun menguning pada tanaman tomat...",
        key="input_field",
        label_visibility="collapsed"
    )
    
    submit_col1, submit_col2, submit_col3 = st.columns([1,6,1])
    with submit_col2:
        submitted = st.form_submit_button("Kirim Pertanyaan", use_container_width=True)

# Proses Input
if submitted and user_input:
    check_daily_reset()
    
    if st.session_state.conversation_count >= 10:
        st.warning("""
            ⚠️ Anda telah mencapai batas 10 percakapan hari ini. 
            Silakan kembali besok untuk bertanya lagi.
        """)
    else:
        if not is_relevant_question(user_input):
            st.warning("""
                Mohon maaf, TaniAI hanya bisa membantu pertanyaan seputar pertanian. 
                Silakan ajukan pertanyaan tentang tanaman, pupuk, hama, atau topik pertanian lainnya.
            """)
        else:
            with st.spinner("🔍 Menganalisis pertanyaan Anda..."):
                try:
                    st.session_state.chat_history.append(("user", user_input))
                    response = chat.send_message(user_input)
                    ai_response = response.text
                    st.session_state.chat_history.append(("ai", ai_response))
                    st.session_state.conversation_count += 1
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {str(e)}")

# Tampilkan Riwayat Chat
if st.session_state.chat_history:
    st.markdown("""
        <div style="margin: 2rem 0 1rem;">
            <h3 style="color: #2e7d32; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.2em;">📜</span> Riwayat Percakapan
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    for role, message in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"""
                <div class="chat-box user-message">
                    <div style="font-weight: 600; color: #0d47a1; margin-bottom: 5px;">Anda:</div>
                    <div>{message}</div>
                </div>
            """, unsafe_allow_html=True)
        elif role == "ai":
            st.markdown(f"""
                <div class="chat-box ai-message">
                    <div style="font-weight: 600; color: #1b5e20; margin-bottom: 5px;">TaniAI:</div>
                    <div>{message}</div>
                </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="margin-top: 3rem; padding: 1.5rem; text-align: center; color: #666; font-size: 0.9rem; border-top: 1px solid #eee;">
        <p>© 2023 TaniAI Pro - Asisten Pertanian Cerdas | Versi 2.1</p>
        <p style="margin-top: 0.5rem;">Dikembangkan dengan ❤️ untuk petani Indonesia</p>
    </div>
""", unsafe_allow_html=True)
