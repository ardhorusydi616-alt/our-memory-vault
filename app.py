import streamlit as st
from supabase import create_client
import uuid
from datetime import datetime

# Koneksi Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Our Memory Vault", page_icon="🎬", layout="wide")

# --- SIDEBAR: UPLOAD ---
with st.sidebar:
    st.header("✨ Tambah Kenangan")
    # Menambah dukungan mp4 dan mov
    uploaded_file = st.file_uploader("Pilih Foto atau Video", type=['png', 'jpg', 'jpeg', 'mp4', 'mov'])
    lokasi = st.text_input("📍 Lokasi momen ini?", placeholder="Misal: Tepi Sungai")
    
    if st.button("Simpan ke Cloud"):
        if uploaded_file and lokasi:
            tgl_skrg = datetime.now().strftime("%d%b%Y")
            ext = uploaded_file.name.split(".")[-1].lower()
            # Format nama: LOKASI_TANGGAL_ID.ekstensi
            file_name = f"{lokasi}_{tgl_skrg}_{uuid.uuid4().hex[:5]}.{ext}"
            
            with st.spinner("Sedang mengupload..."):
                supabase.storage.from_("memories").upload(file_name, uploaded_file.read())
                st.success("Berhasil disimpan!")
                st.rerun()
        else:
            st.warning("Isi lokasi dan pilih file dulu ya!")

# --- HALAMAN UTAMA ---
st.title("🎬 Our Digital Time Capsule")
st.write("Tempat rahasia untuk semua momen foto dan video kita.")

# Ambil daftar file
files = supabase.storage.from_("memories").list()

if not files:
    st.info("Belum ada kenangan. Yuk upload momen pertama kita!")
else:
    # FITUR HAPUS RAPI
    with st.expander("🗑️ Pengaturan Galeri (Hapus File)"):
        list_nama = [f['name'] for f in files]
        file_dipilih = st.selectbox("Pilih file yang ingin dihapus:", list_nama)
        if st.button("Hapus Permanen", type="primary"):
            supabase.storage.from_("memories").remove([file_dipilih])
            st.rerun()

    st.divider()

    # TAMPILAN GALERI (3 KOLOM)
    cols = st.columns(3)
    for idx, file in enumerate(files):
        name = file['name']
        url = supabase.storage.from_("memories").get_public_url(name)
        
        # Pecah nama file untuk ambil lokasi & tgl
        parts = name.split("_")
        disp_loc = parts[0] if len(parts) > 1 else "Memory"
        disp_tgl = parts[1] if len(parts) > 2 else ""

        with cols[idx % 3]:
            # CEK APAKAH VIDEO ATAU FOTO
            if name.lower().endswith(('.mp4', '.mov')):
                st.video(url)
            else:
                st.image(url, use_container_width=True)
            
            st.caption(f"📍 {disp_loc} | 📅 {disp_tgl}")
