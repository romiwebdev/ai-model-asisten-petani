import streamlit as st
import google.generativeai as genai

# Konfigurasi API Key (masukkan di secrets saat deploy)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Inisialisasi model dan chat dengan konteks asisten pertanian
model = genai.GenerativeModel("models/gemini-1.5-flash")
chat = model.start_chat(history=[
    {"role": "user", "parts": ["Kamu adalah asisten virtual pertanian yang membantu petani muda menjawab pertanyaan tentang tanaman, cuaca, pupuk, bibit, dan teknik cocok tanam. Jawablah dengan bahasa yang mudah dimengerti dan ramah."]}
])

# Tampilan Web
st.set_page_config(page_title="Asisten Petani Muda", page_icon="🌱")
st.title("🌾 Asisten Petani Muda (AI)")

st.write("Tanyakan apa pun seputar pertanian, dan AI akan membantu menjawab.")

# Input
with st.form("form_chat"):
    user_input = st.text_input("🧑 Petani:", placeholder="Contoh: Bagaimana cara merawat cabai saat musim hujan?")
    submitted = st.form_submit_button("Kirim")

if submitted and user_input:
    with st.spinner("Sedang memikirkan solusi terbaik..."):
        try:
            response = chat.send_message(user_input)
            st.success("🤖 Asisten AI:")
            st.write(response.text)
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {e}")
