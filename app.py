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

st.title("📄 Turniscanify Watermark Replacer")
st.write("Ubah watermark 'The Contributor Groupy' menjadi 'Turniscanify' dengan presisi.")

# --- FUNGSI UTAMA (LOGIKA KAMU) ---
def process_pdf_in_memory(input_bytes):
    # Membuka PDF langsung dari bytes (memory), bukan dari path file
    doc = fitz.open(stream=input_bytes, filetype="pdf")
    count = 0
    
    # --- PARAMETER FINE TUNING (Sesuai kode kamu) ---
    UKURAN_FONT = 11
    WARNA_CUSTOM = (0.2, 0.2, 0.2) # Hex #333333
    GESER_X = 2  
    GESER_Y = -3.5 
    
    OLD_TEXT = "The Contributor Groupy"
    NEW_TEXT = "Turniscanify"

    # Progress bar sederhana
    progress_bar = st.progress(0)
    total_pages = len(doc)

    for page_num, page in enumerate(doc):
        # Update progress bar
        progress_bar.progress((page_num + 1) / total_pages)

        # 1. Cari teks target
        quads = page.search_for(OLD_TEXT, quads=True)
        
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
            
            # B. Tulis "Turniscanify"
            for q, angle in replacements:
                # Titik mulai dengan geseran
                titik_mulai = fitz.Point(q.ll.x + GESER_X, q.ll.y + GESER_Y)
                
                page.insert_text(
                    titik_mulai,
                    NEW_TEXT,
                    fontsize=UKURAN_FONT,
                    rotate=angle,
                    color=WARNA_CUSTOM,
                    fontname="helv"
                )

    # Kembalikan hasil sebagai bytes (agar bisa didownload)
    return doc.tobytes(), count

# --- UI STREAMLIT ---
uploaded_file = st.file_uploader("Upload File PDF", type=["pdf"])

if uploaded_file is not None:
    # Tampilkan info file
    st.info(f"File terdeteksi: {uploaded_file.name}")
    
    # Tombol Eksekusi
    if st.button("Ubah Watermark Sekarang"):
        try:
            with st.spinner('Sedang memproses...'):
                # Baca file ke memory
                input_bytes = uploaded_file.read()
                
                # Jalankan fungsi
                output_bytes, jumlah_ganti = process_pdf_in_memory(input_bytes)
                
                # --- LOGIKA PENAMAAN DINAMIS ---
                # Ambil nama file asli tanpa ekstensi .pdf
                nama_asli_base, _ = os.path.splitext(uploaded_file.name)
                # Buat nama baru
                nama_baru = f"{nama_asli_base}_By_Turniscanify.pdf"
                
                # Tampilkan Sukses
                st.success(f"Berhasil! {jumlah_ganti} watermark telah diganti.")
                
                # Tombol Download
                st.download_button(
                    label="📥 Download Hasil PDF",
                    data=output_bytes,
                    file_name=nama_baru,
                    mime="application/pdf",
                    type="primary" # Membuat tombol lebih menonjol
                )
                
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

# Footer
st.markdown("---")
st.caption("Powered by PyMuPDF & Streamlit")
