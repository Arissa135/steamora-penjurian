zimport streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="Penjurian Poster STEAMORA 2026", layout="wide", page_icon="🏆")

st.title("🏆 Platform Penjurian Poster Kajian Tindakan STEAMORA 2026")
st.write("Sila pilih nama anda di bar sampingan (sidebar) untuk memulakan pemarkahan.")
st.markdown("---")

# 2. Pautan CSV Google Sheets Anda
SHEET_ID = "1sfwaqs4owcMfzf5f99d0YcuVS4AZNgQ99Pbh72m0obA"
URL_AGIHAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Agihan"

# 3. Baca Data Agihan Juri (Termasuk Lajur Link Poster)
@st.cache_data(ttl=5)
def load_data_agihan():
    df = pd.read_csv(URL_AGIHAN)
    df = df.dropna(how="all").iloc[:, :4]
    df.columns = ["Nama Juri", "ID Poster", "Tajuk Poster", "Link Poster"]
    return df

try:
    df_agihan = load_data_agihan()
except Exception as e:
    st.error(f"⚠️ Ralat membaca data dari Google Sheets: {e}")
    st.info("Pastikan tetapan Google Sheets disetkan kepada 'Anyone with the link can view/edit'.")
    st.stop()

# 4. Kawasan Sidebar (Drop-down Dinamik)
st.sidebar.header("📋 Maklumat Penjurian")

# Drop-down 1: Pilih Nama Juri
senarai_juri = ["-- Pilih Nama Juri --"] + sorted(list(df_agihan["Nama Juri"].astype(str).unique()))
nama_juri_pilihan = st.sidebar.selectbox("Pilih Nama Juri", senarai_juri)

id_poster_pilihan = None
tajuk_poster = ""
link_poster = ""

if nama_juri_pilihan != "-- Pilih Nama Juri --":
    df_juri_poster = df_agihan[df_agihan["Nama Juri"] == nama_juri_pilihan]
    
    # Drop-down 2: Pilih ID Poster milik Juri
    senarai_poster = ["-- Pilih ID Poster --"] + list(df_juri_poster["ID Poster"].astype(str).unique())
    id_poster_pilihan = st.sidebar.selectbox("Pilih ID / Kod Poster", senarai_poster)
    
    # Papar Tajuk & Pautan Poster
    if id_poster_pilihan and id_poster_pilihan != "-- Pilih ID Poster --":
        row_poster = df_juri_poster[df_juri_poster["ID Poster"] == id_poster_pilihan]
        if not row_poster.empty:
            tajuk_poster = row_poster["Tajuk Poster"].values[0]
            link_poster = row_poster["Link Poster"].values[0] if pd.notna(row_poster["Link Poster"].values[0]) else ""
            
            st.sidebar.markdown(f"**Tajuk / Institusi:**\n\n*{tajuk_poster}*")
            
            if link_poster:
                st.sidebar.markdown("---")
                st.sidebar.link_button("📂 Buka / Lihat Poster", str(link_poster), use_container_width=True)

# 5. Rubrik Pemarkahan Lengkap (Point Form Ke Bawah)
rubrik = [
    ("1. Tajuk, Nama Penulis dan Institusi", 3, 
     "* Tajuk jelas dan tepat menggambarkan fokus kajian. [Skor 0-1]\n* Nama dan institusi penulis lengkap dinyatakan. [Skor 0-1]\n* Maklumat penulis disediakan. [Skor 0-1]"),
    
    ("2. Abstrak", 8, 
     "* Masalah kajian jelas dan spesifik. [Skor 0-1]\n* Objektif kajian dirumus dengan tepat. [Skor 0-1]\n* Maklumat peserta diberi dengan lengkap. [Skor 0-1]\n* Intervensi diterangkan dengan jelas. [Skor 0-1]\n* Kaedah pengumpulan data sesuai dan jelas. [Skor 0-1]\n* Dapatan disokong oleh bukti jelas. [Skor 0-2]\n* Kesimpulan berasaskan dapatan kajian. [Skor 0-1]"),
    
    ("3. Latar Belakang Kajian", 7, 
     "* Latar belakang kajian diterangkan lengkap. [Skor 0-2]\n* Masalah dijelaskan dengan mendalam. [Skor 0-2]\n* Bukti awal masalah dikemukakan jelas. [Skor 0-2]\n* Rasional kajian difahami dengan baik. [Skor 0-1]"),
    
    ("4. Objektif Kajian", 7, 
     "* Objektif umum jelas dan berkaitan dengan masalah. [Skor 0-2]\n* Objektif khusus jelas dan boleh diukur. [Skor 0-3]\n* Objektif realistik dan boleh dicapai melalui intervensi. [Skor 0-2]"),
    
    ("5. Intervensi Kajian", 8, 
     "* Masalah dikenal pasti dengan jelas. [Skor 0-1]\n* Perancangan intervensi teratur. [Skor 0-2]\n* Intervensi dilaksanakan dengan sistematik. [Skor 0-2]\n* Pelaksanaan dipantau dengan rapi. [Skor 0-1]\n* Keberkesanan intervensi dinilai. [Skor 0-2]"),
    
    ("6. Metodologi Kajian", 8, 
     "* Penerangan peserta atau kumpulan sasaran lengkap. [Skor 0-2]\n* Tempoh pelaksanaan jelas. [Skor 0-1]\n* Instrumen sesuai untuk kajian. [Skor 0-2]\n* Kaedah pengumpulan data jelas dan tepat. [Skor 0-1]\n* Analisis data sesuai dan jelas. [Skor 0-2]"),
    
    ("7. Dapatan Kajian dan Bukti", 15, 
     "* Dapatan sesuai dengan objektif. [Skor 0-3]\n* Data perbandingan jelas. [Skor 0-3]\n* Perubahan dianalisis dengan tepat. [Skor 0-3]\n* Visual data tepat dan jelas. [Skor 0-2]\n* Tafsiran dibuat berdasarkan bukti. [Skor 0-2]\n* Keberkesanan dibincang dengan baik. [Skor 0-2]"),
    
    ("8. Perubahan yang Diperhatikan dan Refleksi", 6, 
     "* Perubahan peserta diterangkan. [Skor 0-2]\n* Aspek berjaya dan cabaran dibincang. [Skor 0-2]\n* Cadangan diperoleh dari refleksi. [Skor 0-2]"),
    
    ("9. Kesimpulan dan Cadangan", 5, 
     "* Kesimpulan tepat berdasarkan dapatan. [Skor 0-2]\n* Cadangan boleh dilaksanakan. [Skor 0-2]\n* Potensi intervensi dijelaskan. [Skor 0-1]"),
    
    ("10. Kesinambungan dan Keselarasan Kajian", 20, 
     "* Hubungan masalah dengan objektif jelas. [Skor 0-4]\n* Intervensi sesuai dengan objektif. [Skor 0-4]\n* Metodologi dan instrumen sesuai dengan objektif. [Skor 0-4]\n* Dapatan lengkap serta disokong bukti. [Skor 0-5]\n* Kesimpulan tepat dari dapatan. [Skor 0-3]"),
    
    ("11. Rujukan", 4, 
     "* Rujukan relevan dengan kajian. [Skor 0-2]\n* Format APA edisi ke-7 dipatuhi. [Skor 0-1]\n* Petikan dan rujukan konsisten. [Skor 0-1]"),
    
    ("12. Pematuhan Format dan Kelengkapan Kandungan Poster", 5, 
     "* Semua bahagian wajib dalam template lengkap. [Skor 0-3]\n* Susunan kandungan mengikut struktur template. [Skor 0-1]\n* Mematuhi format dan keperluan teknikal. [Skor 0-1]"),
    
    ("13. Kreativiti dan Reka Bentuk Visual", 4, 
     "* Susun atur kemas dan teratur. [Skor 0-1]\n* Teks mudah dibaca dan tiada tipografi. [Skor 0-1]\n* Warna, grafik dan visual yang sesuai. [Skor 0-1]\n* Maklumat disampaikan dengan jelas. [Skor 0-1]")
]

# 6. Borang Pemarkahan Juri
st.subheader("📝 Borang Pemarkahan Juri")

if not nama_juri_pilihan or nama_juri_pilihan == "-- Pilih Nama Juri --" or not id_poster_pilihan or id_poster_pilihan == "-- Pilih ID Poster --":
    st.info("👈 Sila pilih **Nama Juri** dan **ID Poster** di bar sampingan (Sidebar) terlebih dahulu.")
else:
    st.success(f"📌 **Menjuri:** {id_poster_pilihan} | **Juri:** {nama_juri_pilihan}")
    
    # Pautan Poster Utama
    if link_poster:
        st.link_button(f"🔗 Klik Di Sini Untuk Membuka Poster {id_poster_pilihan}", str(link_poster), type="primary")

# Makluman Pemarkahan Perpuluhan & Skala Skor (Rapat Ke Kiri & Teks Hitam)
    st.markdown("""
    <div style="background-color: #FFF9E6; border-left: 5px solid #FFA500; padding: 15px; border-radius: 5px; color: #000000; margin-bottom: 20px;">
        <p style="margin: 0 0 10px 0; color: #000000;">💡 <b>Peringatan Pemarkahan:</b> Markah dalam bentuk <b>nombor perpuluhan</b> (contoh: <code>0.3</code>, <code>1.27</code>, <code>2.5</code>) dibenarkan. Anda boleh <b>menaip terus markah</b> pada ruangan input atau menggunakan <b>butang + / -</b> (selang <code>0.25</code> markah bagi setiap klik).</p>
        <p style="margin: 0 0 10px 0; color: #000000;">💡 Sekiranya penilaian dihantar <b>lebih daripada sekali</b> oleh juri yang sama bagi poster yang sama, hanya penilaian <b>TERKINI</b> akan diambil kira dalam pengiraan markah.</p>
        <p style="margin: 0; color: #000000;"><b>Skala Pemarkahan:</b> Skor Minimum, 0 = Sangat Tidak Setuju |&lt;----------&gt;| Skor Maksimum = Sangat Setuju</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("borang_penjurian"):
        total_score = 0.0

        for kriteria, max_mark, aspek in rubrik:
            c1, c2 = st.columns([3, 1])
            
            with c1:
                st.markdown(f"#### {kriteria} *(Maks: {max_mark})*")
                st.markdown(aspek)
                
            with c2:
                score = st.number_input(
                    label=f"Markah {kriteria}",
                    min_value=0.0,
                    max_value=float(max_mark),
                    step=0.25,
                    key=f"{id_poster_pilihan}_{kriteria}",
                    label_visibility="collapsed"
                )
                total_score += score
            
            st.markdown("---")

        if total_score >= 85:
            pingat = "GOLD"
            badge = "🥇 GOLD"
        elif total_score >= 70:
            pingat = "SILVER"
            badge = "🥈 SILVER"
        else:
            pingat = "BRONZE"
            badge = "🥉 BRONZE"

        st.metric(label="Jumlah Markah Keseluruhan (100)", value=f"{total_score:.2f} / 100")
        st.subheader(f"Keputusan Pingat: {badge}")

        submitted = st.form_submit_button("Hantar & Semak Keputusan", use_container_width=True)

        if submitted:
            st.balloons()
            st.success(f"✅ Keputusan penjurian bagi **{id_poster_pilihan}** disahkan!")
            st.write(f"**Ringkasan Data:** Juri: {nama_juri_pilihan} | ID: {id_poster_pilihan} | Markah: {total_score:.2f} | Pingat: {pingat}")
