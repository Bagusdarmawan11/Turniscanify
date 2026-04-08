import streamlit as st
import fitz  # PyMuPDF
import math
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Turniscanify Watermark Tool",
    page_icon="📄",
    layout="centered"
)

st.title("📄 PDF Watermark Replacer")
st.write("Hapus dan ganti teks watermark pada PDF dengan mudah.")

# --- FUNGSI UTAMA ---
# Sekarang fungsi ini menerima parameter old_text dan new_text dari input user
def process_pdf_in_memory(input_bytes, old_text, new_text):
    doc = fitz.open(stream=input_bytes, filetype="pdf")
    count = 0
    
    # --- STYLE TETAP SEPERTI SEBELUMNYA ---
    UKURAN_FONT = 11
    WARNA_CUSTOM = (0.2, 0.2, 0.2) # Hex #333333
    GESER_X = 2  
    GESER_Y = -3.5 

    progress_bar = st.progress(0)
    total_pages = len(doc)

    for page_num, page in enumerate(doc):
        progress_bar.progress((page_num + 1) / total_pages)

        # 1. Cari teks target sesuai input user
        quads = page.search_for(old_text, quads=True)
        
        replacements = []
        for q in quads:
            p1 = q.ll
            p2 = q.lr
            angle = math.degrees(math.atan2(p2.y - p1.y, p2.x - p1.x))
            replacements.append((q, angle))
            count += 1

        # 2. Eksekusi
        if replacements:
            # A. Hapus teks lama
            for q, _ in replacements:
                rect_hapus = fitz.Rect(q.ul.x, q.ul.y - 2, q.lr.x, q.lr.y + 2)
                page.add_redact_annot(rect_hapus)
            page.apply_redactions()
            
            # B. Tulis Teks Baru sesuai input user
            for q, angle in replacements:
                titik_mulai = fitz.Point(q.ll.x + GESER_X, q.ll.y + GESER_Y)
                
                page.insert_text(
                    titik_mulai,
                    new_text,
                    fontsize=UKURAN_FONT,
                    rotate=angle,
                    color=WARNA_CUSTOM,
                    fontname="helv"
                )

    return doc.tobytes(), count

# --- UI STREAMLIT ---
# Membagi layar jadi 2 kolom agar rapi
col1, col2 = st.columns(2)
with col1:
    input_teks_lama = st.text_input("Teks yang ingin dihapus:", value="The Contributor Groupy")
with col2:
    input_teks_baru = st.text_input("Teks pengganti:", value="Turniscanify")

uploaded_file = st.file_uploader("Upload File PDF", type=["pdf"])

if uploaded_file is not None:
    st.info(f"File terdeteksi: {uploaded_file.name}")
    
    # Tombol Eksekusi
    if st.button("Ubah Watermark Sekarang"):
        # Validasi: Pastikan form tidak kosong
        if not input_teks_lama or not input_teks_baru:
            st.warning("Mohon isi teks yang ingin dihapus dan teks penggantinya terlebih dahulu.")
        else:
            try:
                with st.spinner('Sedang memproses...'):
                    input_bytes = uploaded_file.read()
                    
                    # Jalankan fungsi dengan teks dari user
                    output_bytes, jumlah_ganti = process_pdf_in_memory(
                        input_bytes, 
                        input_teks_lama, 
                        input_teks_baru
                    )
                    
                    # --- NAMA FILE DINAMIS ---
                    nama_asli_base, _ = os.path.splitext(uploaded_file.name)
                    # Nama file akan menggunakan input teks baru tanpa spasi yang berlebihan
                    nama_baru_clean = input_teks_baru.replace(" ", "_")
                    nama_baru = f"{nama_asli_base}_By_{nama_baru_clean}.pdf"
                    
                    if jumlah_ganti > 0:
                        st.success(f"Berhasil! {jumlah_ganti} bagian teks telah diganti.")
                        
                        st.download_button(
                            label="📥 Download Hasil PDF",
                            data=output_bytes,
                            file_name=nama_baru,
                            mime="application/pdf",
                            type="primary"
                        )
                    else:
                        st.warning(f"Selesai diproses, tapi teks '{input_teks_lama}' tidak ditemukan di dalam PDF ini.")
                    
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

# Footer
st.markdown("---")
st.caption("Powered by PyMuPDF & Streamlit")
