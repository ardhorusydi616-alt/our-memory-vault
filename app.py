import streamlit as st
from supabase import create_client
import uuid
from datetime import datetime

# Koneksi Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Our Memory Vault", page_icon="📸")

# --- SIDEBAR: UPLOAD ---
with st.sidebar:
    st.header("✨ Tambah Kenangan")
    uploaded_file = st.file_uploader("Pilih Foto", type=['png', 'jpg', 'jpeg'])
    lokasi = st.text_input("📍 Lokasi momen ini?", placeholder="Misal: Kantin UTY")
    
    if st.button("Simpan ke Cloud"):
        if uploaded_file and lokasi:
            tgl_skrg = datetime.now().strftime("%d%b%Y")
            # Format nama: LOKASI_TANGGAL_ID.jpg
            file_name = f"{lokasi}_{tgl_skrg}_{uuid.uuid4().hex[:5]}.jpg"
            
            supabase.storage.from_("memories").upload(file_name, uploaded_file.read())
            st.success("Berhasil disimpan!")
            st.rerun()

# --- HALAMAN UTAMA ---
st.title("📸 Our Digital Time Capsule")

files = supabase.storage.from_("memories").list()

if not files:
    st.info("Belum ada foto. Yuk upload momen pertama kita!")
else:
    # FITUR HAPUS RAPI
    with st.expander("🗑️ Pengaturan Galeri (Hapus Foto)"):
        list_nama = [f['name'] for f in files]
        file_dipilih = st.selectbox("Pilih file yang ingin dihapus:", list_nama)
        if st.button("Hapus Permanen", type="primary"):
            supabase.storage.from_("memories").remove([file_dipilih])
            st.rerun()

    st.divider()

    # TAMPILAN GALERI
    cols = st.columns(3)
    for idx, file in enumerate(files):
        name = file['name']
        url = supabase.storage.from_("memories").get_public_url(name)
        
        # Pecah nama file untuk ambil lokasi & tgl
        parts = name.split("_")
        disp_loc = parts[0] if len(parts) > 1 else "Memory"
        disp_tgl = parts[1] if len(parts) > 2 else ""

        with cols[idx % 3]:
            st.image(url, use_container_width=True)
            st.caption(f"📍 {disp_loc} | 📅 {disp_tgl}")
