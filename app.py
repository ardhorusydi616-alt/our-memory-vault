import streamlit as st
from supabase import create_client
import uuid

# MENGAMBIL DATA DARI SECRETS STREAMLIT (LEBIH AMAN & STABIL)
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Our Memory Vault", page_icon="📸")

# Estetika CSS
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    .stHeader { border-bottom: 2px solid #ff4b4b; }
    </style>
""", unsafe_allow_html=True)

st.title("📸 Our Digital Time Capsule")
st.write("Tempat rahasia untuk semua momen kita.")

# --- FITUR UPLOAD ---
with st.sidebar:
    st.header("✨ Tambah Kenangan")
    uploaded_file = st.file_uploader("Pilih Foto/Video", type=['png', 'jpg', 'jpeg', 'mp4'])
    if st.button("Upload ke Cloud"):
        if uploaded_file:
            # Membuat nama file unik
            file_extension = uploaded_file.name.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            
            # Proses Upload
            res = supabase.storage.from_("memories").upload(file_name, uploaded_file.read())
            st.success("Berhasil disimpan di awan!")
            st.rerun()

# --- FITUR DISPLAY (GALLERY) ---
st.subheader("🖼️ Galeri Bersama")
files = supabase.storage.from_("memories").list()

if not files:
    st.info("Belum ada kenangan. Yuk, upload foto pertama kita!")
else:
    # Menampilkan file dalam grid
    cols = st.columns(3)
    for idx, file in enumerate(files):
        public_url = supabase.storage.from_("memories").get_public_url(file['name'])
        with cols[idx % 3]:
            if file['name'].endswith('.mp4'):
                st.video(public_url)
            else:
                st.image(public_url, use_container_width=True)
