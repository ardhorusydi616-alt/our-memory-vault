import streamlit as st
from supabase import create_client
import uuid
from datetime import datetime

# Koneksi Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Our Memory Vault", page_icon="📸", layout="wide")

# --- SIDEBAR: UPLOAD ---
with st.sidebar:
    st.header("✨ Tambah Kenangan")
    uploaded_file = st.file_uploader("Pilih Foto/Video", type=['png', 'jpg', 'jpeg', 'mp4'])
    lokasi = st.text_input("📍 Di mana momen ini diambil?", placeholder="Misal: Warung Ramen")
    
    if st.button("Simpan ke Cloud"):
        if uploaded_file and lokasi:
            file_extension = uploaded_file.name.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            
            # Menambahkan Metadata (Tanggal & Lokasi)
            metadata = {
                "location": lokasi,
                "upload_date": datetime.now().strftime("%d %b %Y, %H:%M")
            }
            
            res = supabase.storage.from_("memories").upload(
                file_name, 
                uploaded_file.read(),
                file_options={"x-upsert": "false", "metadata": metadata}
            )
            st.success("Berhasil disimpan!")
            st.rerun()
        else:
            st.warning("Pilih file dan isi lokasinya dulu ya!")

# --- HALAMAN UTAMA: GALERI ---
st.title("📸 Our Digital Time Capsule")
files = supabase.storage.from_("memories").list(options={"sort_by": {"column": "created_at", "order": "desc"}})

if not files:
    st.info("Belum ada kenangan. Yuk, upload foto pertama kita!")
else:
    # 1. LOGIKA PILIH UNTUK HAPUS
    with st.expander("🗑️ Pengaturan Galeri (Hapus Foto)"):
        list_nama_file = [f['name'] for f in files]
        file_dipilih = st.selectbox("Pilih file yang ingin dihapus:", list_nama_file)
        if st.button("Konfirmasi Hapus", type="primary"):
            supabase.storage.from_("memories").remove([file_dipilih])
            st.success(f"File {file_dipilih} berhasil dihapus!")
            st.rerun()

    st.divider()

    # 2. TAMPILAN GALERI
    cols = st.columns(3)
    for idx, file in enumerate(files):
        file_name = file['name']
        public_url = supabase.storage.from_("memories").get_public_url(file_name)
        
        # Ambil Metadata (Jika ada)
        info = file.get('metadata', {})
        tgl = info.get('upload_date', "Tanggal tidak tercatat")
        loc = info.get('location', "Lokasi tidak tercatat")
        
        with cols[idx % 3]:
            st.image(public_url, use_container_width=True)
            st.caption(f"📍 {loc}  \n📅 {tgl}")
