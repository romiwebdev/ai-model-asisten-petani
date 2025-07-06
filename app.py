import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import time
import json
import pandas as pd
import numpy as np
import pytz
from PIL import Image
import requests
from io import BytesIO
import sqlite3
import hashlib
import os

# ----------------------------
# KONFIGURASI DASAR
# ----------------------------

# Konfigurasi API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_NAME = "models/gemini-1.5-pro-latest"

# Konfigurasi Basis Data
DB_NAME = "taniai_database.db"
IMAGE_CACHE_DIR = "image_cache"

# Buat direktori cache jika belum ada
os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

# ----------------------------
# MODEL AI & FUNGSI UTAMA
# ----------------------------

class AgriculturalAI:
    def __init__(self):
        self.model = genai.GenerativeModel(MODEL_NAME)
        self.system_prompt = """
        Anda adalah TaniAI - Asisten Pertanian Digital dengan spesialisasi:
        1. Diagnosis tanaman berdasarkan gejala
        2. Rekomendasi pola tanam berdasarkan lokasi
        3. Analisis pasar hasil pertanian
        4. Prediksi cuaca untuk pertanian
        5. Pengelolaan hama & penyakit tanaman
        6. Teknik pertanian presisi
        
        Aturan respons:
        - Gunakan bahasa Indonesia yang mudah dipahami
        - Sertakan data pendukung ketika memungkinkan
        - Untuk pertanyaan kompleks, berikan jawaban bertahap
        - Jika memerlukan gambar, minta detail tambahan
        - Untuk diagnosis, gunakan pendekatan langkah-demi-langkah
        - Selalu verifikasi informasi dengan sumber terpercaya
        """
        self.chat = self.model.start_chat(history=[])
        
    def query(self, prompt, image=None):
        try:
            if image:
                response = self.chat.send_message([prompt, image])
            else:
                response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

# ----------------------------
# MANAJEMEN BASIS DATA
# ----------------------------

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self._init_db()
        
    def _init_db(self):
        cursor = self.conn.cursor()
        
        # Tabel Pengguna
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            location TEXT,
            farming_type TEXT,
            register_date TEXT,
            last_active TEXT
        )
        """)
        
        # Tabel Percakapan
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conv_id TEXT PRIMARY KEY,
            user_id TEXT,
            timestamp TEXT,
            user_input TEXT,
            ai_response TEXT,
            topic_category TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        """)
        
        # Tabel Batas Penggunaan
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_limits (
            user_id TEXT PRIMARY KEY,
            daily_count INTEGER,
            last_reset TEXT,
            total_usage INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        """)
        
        # Tabel Penyakit Tanaman
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plant_diseases (
            disease_id TEXT PRIMARY KEY,
            name TEXT,
            symptoms TEXT,
            treatment TEXT,
            prevention TEXT,
            affected_plants TEXT
        )
        """)
        
        self.conn.commit()
    
    def log_conversation(self, user_id, user_input, ai_response, category):
        conv_id = hashlib.md5(f"{user_id}{datetime.now()}".encode()).hexdigest()
        timestamp = datetime.now(pytz.timezone('Asia/Jakarta')).isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO conversations VALUES (?, ?, ?, ?, ?, ?)",
            (conv_id, user_id, timestamp, user_input, ai_response, category)
        )
        self.conn.commit()
        
    def get_user_usage(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT daily_count, last_reset FROM usage_limits WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return result
        else:
            # Inisialisasi pengguna baru
            now = datetime.now(pytz.timezone('Asia/Jakarta')).date().isoformat()
            cursor.execute(
                "INSERT INTO usage_limits VALUES (?, ?, ?, ?)",
                (user_id, 0, now, 0)
            )
            self.conn.commit()
            return (0, now)
    
    def update_usage(self, user_id):
        today = datetime.now(pytz.timezone('Asia/Jakarta')).date().isoformat()
        current_usage = self.get_user_usage(user_id)
        
        if current_usage[1] != today:
            # Reset harian
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE usage_limits SET daily_count = 1, last_reset = ?, total_usage = total_usage + 1 WHERE user_id = ?",
                (today, user_id)
            )
        else:
            # Tambah penggunaan
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE usage_limits SET daily_count = daily_count + 1, total_usage = total_usage + 1 WHERE user_id = ?",
                (user_id,))
        
        self.conn.commit()

# ----------------------------
# MODUL ANALISIS PERTANIAN
# ----------------------------

class AgriculturalAnalytics:
    @staticmethod
    def analyze_soil_conditions(ph_level, moisture, nutrients):
        """Analisis kondisi tanah berdasarkan parameter"""
        conditions = []
        
        # Analisis pH
        if ph_level < 5.5:
            conditions.append(("Keasaman Tanah", "Terlalu asam", "Tambahkan kapur pertanian"))
        elif ph_level > 7.5:
            conditions.append(("Keasaman Tanah", "Terlalu basa", "Tambahkan belerang atau bahan organik"))
        else:
            conditions.append(("Keasaman Tanah", "Optimal", "Pertahankan"))
        
        # Analisis kelembaban
        if moisture < 30:
            conditions.append(("Kelembaban", "Terlalu kering", "Perbaiki irigasi dan tambahkan mulsa"))
        elif moisture > 70:
            conditions.append(("Kelembaban", "Terlalu basah", "Perbaiki drainase"))
        else:
            conditions.append(("Kelembaban", "Optimal", "Pertahankan"))
        
        # Analisis nutrisi
        npk_ratio = nutrients.get('npk_ratio', (1,1,1))
        if npk_ratio[0] < 0.5:
            conditions.append(("Nitrogen", "Defisiensi", "Tambahkan pupuk nitrogen seperti urea"))
        if npk_ratio[1] < 0.3:
            conditions.append(("Fosfor", "Defisiensi", "Tambahkan pupuk fosfat"))
        if npk_ratio[2] < 0.4:
            conditions.append(("Kalium", "Defisiensi", "Tambahkan pupuk kalium"))
        
        return pd.DataFrame(conditions, columns=["Parameter", "Kondisi", "Rekomendasi"])

# ----------------------------
# MANAJEMEN SESSION & STATE
# ----------------------------

class SessionState:
    def __init__(self):
        self.user_id = None
        self.user_profile = None
        self.conversation_history = []
        self.current_topic = None
        self.daily_usage = 0
        self.last_reset = None
        
        # Inisialisasi komponen utama
        self.ai_engine = AgriculturalAI()
        self.db_manager = DatabaseManager()
        
    def initialize_user(self, user_id):
        """Inisialisasi data pengguna"""
        self.user_id = user_id
        self._load_user_data()
        
    def _load_user_data(self):
        """Memuat data pengguna dari database"""
        cursor = self.db_manager.conn.cursor()
        
        # Cek apakah pengguna sudah terdaftar
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (self.user_id,))
        user_data = cursor.fetchone()
        
        if user_data:
            self.user_profile = {
                "name": user_data[1],
                "location": user_data[2],
                "farming_type": user_data[3]
            }
        else:
            # Pengguna baru
            self.user_profile = {
                "name": "Petani",
                "location": None,
                "farming_type": None
            }
            cursor.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                (self.user_id, "Petani", None, None, 
                 datetime.now(pytz.timezone('Asia/Jakarta')).isoformat(),
                 datetime.now(pytz.timezone('Asia/Jakarta')).isoformat())
            )
            self.db_manager.conn.commit()
        
        # Muat data penggunaan
        usage_data = self.db_manager.get_user_usage(self.user_id)
        self.daily_usage = usage_data[0]
        self.last_reset = usage_data[1]

# ----------------------------
# FUNGSI UTILITAS
# ----------------------------

def get_user_id():
    """Generate unique user ID based on browser and IP"""
    try:
        user_agent = st.experimental_get_query_params().get("user_agent", [""])[0]
        ip_address = st.experimental_get_query_params().get("ip", ["anonymous"])[0]
        return hashlib.md5(f"{user_agent}{ip_address}".encode()).hexdigest()
    except:
        return "default_user"

def save_uploaded_image(uploaded_file):
    """Simpan gambar yang diunggah ke cache"""
    image_hash = hashlib.md5(uploaded_file.read()).hexdigest()
    file_path = os.path.join(IMAGE_CACHE_DIR, f"{image_hash}.jpg")
    
    uploaded_file.seek(0)  # Kembali ke awal file setelah membaca
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
        
    return file_path

def analyze_plant_image(image_path):
    """Analisis gambar tanaman menggunakan model AI"""
    try:
        img = Image.open(image_path)
        st.image(img, caption="Gambar yang Diunggah", width=300)
        
        with st.spinner("🔍 Menganalisis gambar tanaman..."):
            # Simulasi analisis (dalam implementasi nyata, gunakan model CV)
            time.sleep(2)
            return {
                "health_status": "Sehat" if np.random.random() > 0.3 else "Terinfeksi",
                "disease_probability": round(np.random.random() * 100, 2),
                "recommendations": [
                    "Periksa kelembaban tanah secara teratur",
                    "Berikan pupuk seimbang",
                    "Pantau perkembangan gejala"
                ]
            }
    except Exception as e:
        st.error(f"Gagal menganalisis gambar: {str(e)}")
        return None

# ----------------------------
# ANTARMUKA PENGGUNA
# ----------------------------

def setup_ui():
    """Konfigurasi antarmuka Streamlit"""
    st.set_page_config(
        page_title="TaniAI Pro - Asisten Pertanian Digital",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
            .main {
                background-color: #f5f9f4;
            }
            .sidebar .sidebar-content {
                background-color: #e8f5e9;
            }
            .stButton>button {
                background-color: #2e7d32;
                color: white;
                border-radius: 20px;
                padding: 10px 24px;
            }
            .stTextInput>div>div>input {
                border-radius: 20px;
                padding: 12px;
            }
            .stFileUploader>div>div>button {
                border-radius: 20px;
            }
            .chat-message {
                padding: 12px 16px;
                border-radius: 12px;
                margin: 8px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .user-message {
                background-color: #e3f2fd;
                margin-left: 20%;
            }
            .ai-message {
                background-color: #f1f8e9;
                margin-right: 20%;
            }
            .warning-box {
                background-color: #fff3e0;
                padding: 12px;
                border-radius: 8px;
                border-left: 4px solid #ffa000;
                margin: 12px 0;
            }
        </style>
    """, unsafe_allow_html=True)

def show_user_profile(state):
    """Tampilkan dan edit profil pengguna"""
    with st.sidebar.expander("📝 Profil Saya", expanded=True):
        name = st.text_input("Nama", value=state.user_profile["name"])
        location = st.text_input("Lokasi Pertanian", value=state.user_profile["location"] or "")
        farming_type = st.selectbox(
            "Jenis Pertanian",
            ["Padi", "Sayuran", "Buah", "Perkebunan", "Hidroponik", "Lainnya"],
            index=0 if not state.user_profile["farming_type"] else ["Padi", "Sayuran", "Buah", "Perkebunan", "Hidroponik", "Lainnya"].index(state.user_profile["farming_type"])
        )
        
        if st.button("Simpan Profil"):
            state.user_profile.update({
                "name": name,
                "location": location,
                "farming_type": farming_type
            })
            
            cursor = state.db_manager.conn.cursor()
            cursor.execute(
                "UPDATE users SET name = ?, location = ?, farming_type = ? WHERE user_id = ?",
                (name, location, farming_type, state.user_id)
            )
            state.db_manager.conn.commit()
            st.success("Profil diperbarui!")

def show_usage_stats(state):
    """Tampilkan statistik penggunaan"""
    with st.sidebar.expander("📊 Statistik Penggunaan", expanded=True):
        st.metric("Percakapan Hari Ini", f"{state.daily_usage}/10")
        st.progress(state.daily_usage / 10)
        
        cursor = state.db_manager.conn.cursor()
        cursor.execute(
            "SELECT total_usage FROM usage_limits WHERE user_id = ?",
            (state.user_id,)
        )
        total_usage = cursor.fetchone()[0]
        st.metric("Total Percakapan", total_usage)
        
        # Analisis topik populer
        cursor.execute(
            "SELECT topic_category, COUNT(*) as count FROM conversations WHERE user_id = ? GROUP BY topic_category ORDER BY count DESC LIMIT 3",
            (state.user_id,)
        )
        popular_topics = cursor.fetchall()
        
        if popular_topics:
            st.write("**Topik Favorit Anda:**")
            for topic, count in popular_topics:
                st.write(f"- {topic or 'Umum'} ({count}x)")

def show_agricultural_tools(state):
    """Tampilkan alat bantu pertanian"""
    with st.sidebar.expander("🛠 Alat Pertanian", expanded=True):
        tab1, tab2, tab3 = st.tabs(["Tanah", "Tanaman", "Pasar"])
        
        with tab1:
            st.subheader("Analisis Tanah")
            ph_level = st.slider("pH Tanah", 3.0, 9.0, 6.5, 0.1)
            moisture = st.slider("Kelembaban Tanah (%)", 0, 100, 50)
            npk_n = st.slider("Nitrogen (N)", 0, 100, 50)
            npk_p = st.slider("Fosfor (P)", 0, 100, 30)
            npk_k = st.slider("Kalium (K)", 0, 100, 40)
            
            if st.button("Analisis Kondisi Tanah"):
                soil_data = {
                    'ph_level': ph_level,
                    'moisture': moisture,
                    'npk_ratio': (npk_n/100, npk_p/100, npk_k/100)
                }
                analysis = AgriculturalAnalytics.analyze_soil_conditions(**soil_data)
                st.dataframe(analysis, hide_index=True)
        
        with tab2:
            st.subheader("Diagnosis Tanaman")
            uploaded_image = st.file_uploader("Unggah Gambar Tanaman", type=["jpg", "png"])
            
            if uploaded_image:
                image_path = save_uploaded_image(uploaded_image)
                analysis = analyze_plant_image(image_path)
                
                if analysis:
                    st.write(f"**Status Kesehatan:** {analysis['health_status']}")
                    st.write(f"**Kemungkinan Penyakit:** {analysis['disease_probability']}%")
                    st.write("**Rekomendasi:**")
                    for rec in analysis["recommendations"]:
                        st.write(f"- {rec}")
        
        with tab3:
            st.subheader("Harga Pasar")
            commodity = st.selectbox("Pilih Komoditas", ["Beras", "Jagung", "Kedelai", "Cabai", "Bawang Merah"])
            if st.button("Cek Harga"):
                # Simulasi data harga (dalam implementasi nyata, gunakan API)
                prices = {
                    "Beras": "Rp 12.000 - Rp 15.000/kg",
                    "Jagung": "Rp 8.000 - Rp 10.000/kg",
                    "Kedelai": "Rp 15.000 - Rp 18.000/kg",
                    "Cabai": "Rp 25.000 - Rp 50.000/kg",
                    "Bawang Merah": "Rp 30.000 - Rp 45.000/kg"
                }
                st.success(f"Harga {commodity} saat ini: {prices[commodity]}")

# ----------------------------
# FUNGSI UTAMA APLIKASI
# ----------------------------

def main():
    setup_ui()
    
    # Inisialisasi state
    user_id = get_user_id()
    state = SessionState()
    state.initialize_user(user_id)
    
    # Sidebar
    st.sidebar.image("https://via.placeholder.com/150x50?text=TaniAI+Pro", use_column_width=True)
    show_user_profile(state)
    show_usage_stats(state)
    show_agricultural_tools(state)
    
    # Konten utama
    st.title("🌱 TaniAI Pro - Asisten Pertanian Digital")
    st.write("""
        Selamat datang di asisten pertanian digital paling canggih. Tanyakan apa saja seputar pertanian, 
        dari teknik budidaya hingga analisis pasar. Mulai percakapan di bawah ini!
    """)
    
    # Tab utama
    main_tab, history_tab = st.tabs(["💬 Chat", "📜 Riwayat"])
    
    with main_tab:
        # Form input pengguna
        with st.form("chat_form"):
            cols = st.columns([4, 1])
            with cols[0]:
                user_input = st.text_input(
                    "Tanyakan tentang pertanian...",
                    placeholder="Contoh: Bagaimana mengatasi hama wereng pada padi?",
                    label_visibility="collapsed"
                )
            with cols[1]:
                submitted = st.form_submit_button("Kirim")
            
            # Unggah gambar untuk diagnosis
            uploaded_image = st.file_uploader(
                "Atau unggah gambar tanaman untuk diagnosis",
                type=["jpg", "png", "jpeg"],
                accept_multiple_files=False,
                key="image_uploader"
            )
        
        # Proses input
        if submitted and (user_input or uploaded_image):
            # Periksa batas penggunaan
            if state.daily_usage >= 10:
                st.warning("""
                    ⚠️ Anda telah mencapai batas 10 percakapan hari ini. 
                    Fitur premium akan datang segera dengan akses tidak terbatas!
                """)
            else:
                with st.spinner("🔍 Menganalisis pertanyaan Anda..."):
                    try:
                        # Proses gambar jika ada
                        image_path = None
                        if uploaded_image:
                            image_path = save_uploaded_image(uploaded_image)
                            img = Image.open(image_path)
                            
                        # Dapatkan respons AI
                        if image_path and user_input:
                            response = state.ai_engine.query(user_input, img)
                        elif image_path:
                            response = state.ai_engine.query("Berikan diagnosis untuk tanaman dalam gambar ini", img)
                        else:
                            response = state.ai_engine.query(user_input)
                        
                        # Perbarui state
                        state.conversation_history.append(("user", user_input))
                        state.conversation_history.append(("ai", response))
                        state.db_manager.log_conversation(
                            state.user_id, 
                            user_input, 
                            response, 
                            "Diagnosis" if uploaded_image else "Umum"
                        )
                        state.db_manager.update_usage(state.user_id)
                        state.daily_usage += 1
                        
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {str(e)}")
        
        # Tampilkan riwayat percakapan
        for role, message in state.conversation_history:
            if role == "user" and message:
                st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>Anda:</strong><br>
                        {message}
                    </div>
                """, unsafe_allow_html=True)
            elif role == "ai" and message:
                st.markdown(f"""
                    <div class="chat-message ai-message">
                        <strong>TaniAI:</strong><br>
                        {message}
                    </div>
                """, unsafe_allow_html=True)
    
    with history_tab:
        st.subheader("Riwayat Percakapan")
        cursor = state.db_manager.conn.cursor()
        cursor.execute(
            "SELECT timestamp, user_input, ai_response FROM conversations WHERE user_id = ? ORDER BY timestamp DESC",
            (state.user_id,)
        history = cursor.fetchall()
        
        if history:
            for timestamp, user_input, ai_response in history:
                dt = datetime.fromisoformat(timestamp)
                st.write(f"**{dt.strftime('%d %b %Y %H:%M')}**")
                with st.expander(user_input[:50] + "..." if len(user_input) > 50 else user_input):
                    st.markdown(f"**Anda:** {user_input}")
                    st.markdown(f"**TaniAI:** {ai_response}")
                st.divider()
        else:
            st.info("Belum ada riwayat percakapan")

if __name__ == "__main__":
    main()
