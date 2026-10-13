import streamlit as st
import pandas as pd

# ============================================================
# 1. KONFIGURASI HALAMAN
# ============================================================

st.set_page_config(
    page_title="Proyek Berkom 12 | Pencarian Kost Ideal",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM DESIGN: SAGE GREEN + CREAM
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
    --sage-dark: #355640;
    --sage: #55785d;
    --sage-light: #e7eee3;
    --cream: #f7f7f1;
    --ink: #26382c;
    --muted: #68796b;
}

.stApp {
    background: var(--cream);
    color: var(--ink);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] { background: rgba(247,247,241,0.88); }
.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: var(--sage-dark) !important;
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: -0.035em;
}

p, label, .stMarkdown { color: var(--ink); }
[data-testid="stCaptionContainer"] { color: var(--muted); }

[data-testid="stSidebar"] {
    background: #eaf0e6;
    border-right: 1px solid #d9e3d5;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--sage-dark) !important; }

.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    background: var(--sage-dark);
    color: #fff;
    border: 1px solid var(--sage-dark);
    border-radius: 12px;
    min-height: 2.7rem;
    font-weight: 700;
    transition: all .18s ease-in-out;
}
.stButton > button:hover, .stFormSubmitButton > button:hover,
.stDownloadButton > button:hover {
    background: #263f2e;
    color: #fff;
    border-color: #263f2e;
    transform: translateY(-1px);
}

[data-testid="stMetric"] {
    background: #fff;
    border: 1px solid #e2e8dd;
    border-radius: 16px;
    padding: 16px 18px;
    box-shadow: 0 4px 18px rgba(45, 68, 48, .035);
}
[data-testid="stMetricLabel"] { color: var(--muted); }
[data-testid="stMetricValue"] { color: var(--sage-dark); font-family: 'Manrope', sans-serif; }

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px;
    border-color: #dfe7da;
    background: rgba(255,255,255,.72);
}

.stTextInput input, .stNumberInput input, .stTextArea textarea,
[data-baseweb="select"] > div {
    border-radius: 10px !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #dfe7da;
    border-radius: 14px;
    overflow: hidden;
}

hr { border-color: #dfe6d9; }

[data-testid="stAlert"] { border-radius: 13px; }

.kost-hero {
    background: linear-gradient(125deg, #e4ecdf 0%, #f2f3e9 65%, #f8f7ef 100%);
    border: 1px solid #dbe5d5;
    border-radius: 24px;
    padding: 34px 36px;
    margin: 0 0 24px 0;
}
.kost-eyebrow {
    color: #55785d;
    font-size: .76rem;
    font-weight: 800;
    letter-spacing: .13em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.kost-hero-title {
    color: #304b38;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(2rem, 4vw, 3.2rem);
    line-height: 1.12;
    letter-spacing: -.055em;
    font-weight: 800;
    margin: 0 0 12px 0;
}
.kost-hero-copy {
    color: #526655;
    font-size: 1.02rem;
    max-width: 650px;
    line-height: 1.7;
    margin: 0;
}
.kost-section-label {
    color: #6b806d;
    font-size: .76rem;
    font-weight: 800;
    letter-spacing: .11em;
    text-transform: uppercase;
}

@media (max-width: 700px) {
    .block-container { padding-top: 1rem; }
    .kost-hero { padding: 24px 22px; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='kost-eyebrow'>KOST12 · SMART KOST FINDER</div>", unsafe_allow_html=True)
st.caption("Temukan tempat tinggal yang cocok dengan kebutuhan, budget, dan gaya hidupmu.")

# ============================================================
# 2. DATA AWAL
# ============================================================

if "daftar_kost" not in st.session_state:
    st.session_state.daftar_kost = []

if "kriteria" not in st.session_state:
    st.session_state.kriteria = {
        "harga_maks": 1_500_000,
        "jarak_maks": 3.0,
        "luas_min": 10.0,
        "ac": False,
        "kamar_mandi": False,
        "furnished": False,
        "parkir": False,
        "ruang_hijau": False,
        "transportasi": False,
    }

daftar_kost = st.session_state.daftar_kost

# ============================================================
# 3. FUNGSI BANTUAN
# ============================================================

def format_rupiah(nilai):
    return f"Rp{nilai:,.0f}".replace(",", ".")


def hitung_skor(kost):
    # Skor harga: semakin murah, semakin tinggi skornya.
    if kost["harga"] <= 1_000_000:
        skor_harga = 3
    elif kost["harga"] <= 1_500_000:
        skor_harga = 2
    else:
        skor_harga = 1

    # Skor jarak: semakin dekat, semakin tinggi skornya.
    if kost["jarak"] <= 1:
        skor_jarak = 3
    elif kost["jarak"] <= 2:
        skor_jarak = 2
    else:
        skor_jarak = 1

    # Skor luas kamar.
    if kost["luas"] >= 18:
        skor_luas = 3
    elif kost["luas"] >= 14:
        skor_luas = 2
    else:
        skor_luas = 1

    # Skor fasilitas kamar.
    fasilitas_kamar = [
        kost["ac"],
        kost["kamar_mandi"],
        kost["furnished"],
    ]
    jumlah_fasilitas_kamar = sum(fasilitas_kamar)

    if jumlah_fasilitas_kamar == 3:
        skor_fasilitas = 3
    elif jumlah_fasilitas_kamar == 2:
        skor_fasilitas = 2
    else:
        skor_fasilitas = 1

    # Skor fasilitas lingkungan.
    fasilitas_lingkungan = [
        kost["parkir"],
        kost["ruang_hijau"],
        kost["transportasi"],
    ]
    jumlah_fasilitas_lingkungan = sum(fasilitas_lingkungan)

    if jumlah_fasilitas_lingkungan == 3:
        skor_lingkungan = 3
    elif jumlah_fasilitas_lingkungan == 2:
        skor_lingkungan = 2
    else:
        skor_lingkungan = 1

    # Bobot setiap kategori, mengikuti program awal.
    total = (
        skor_harga * 3
        + skor_jarak * 2
        + skor_luas * 2
        + skor_fasilitas
        + skor_lingkungan
    )

    return {
        "harga": skor_harga,
        "jarak": skor_jarak,
        "luas": skor_luas,
        "fasilitas": skor_fasilitas,
        "lingkungan": skor_lingkungan,
        "total": total,
    }


def cari_kost():
    hasil = []
    kriteria = st.session_state.kriteria

    for kost in st.session_state.daftar_kost:
        # Kamar harus masih tersedia.
        if kost["kamar_tersisa"] <= 0:
            continue

        # Saring berdasarkan harga, jarak, dan luas.
        if kost["harga"] > kriteria["harga_maks"]:
            continue
        if kost["jarak"] > kriteria["jarak_maks"]:
            continue
        if kost["luas"] < kriteria["luas_min"]:
            continue

        # Saring berdasarkan fasilitas yang diwajibkan.
        fasilitas_wajib = [
            "ac",
            "kamar_mandi",
            "furnished",
            "parkir",
            "ruang_hijau",
            "transportasi",
        ]

        lolos = True
        for fasilitas in fasilitas_wajib:
            if kriteria[fasilitas] and not kost[fasilitas]:
                lolos = False
                break

        if lolos:
            hasil.append({
                "kost": kost,
                "skor": hitung_skor(kost),
            })

    hasil.sort(key=lambda item: item["skor"]["total"], reverse=True)
    return hasil


# ============================================================
# 4. NAVIGASI
# ============================================================

with st.sidebar:
    st.markdown("## 🏡 kost12.")
    st.caption("Pencarian kost yang lebih mudah")
    st.divider()
    st.markdown("#### MENU")
    halaman = st.radio(
        "Pilih halaman:",
        [
            "Beranda",
            "Cari dan Ranking Kost",
            "Tambah Data Kost",
            "Lihat Seluruh Data",
            "Ubah Kriteria",
            "Tutorial",
        ],
    )

    st.divider()
    st.metric("Total data kost", len(st.session_state.daftar_kost))
    st.caption("Data tersimpan selama sesi aplikasi berjalan.")

# ============================================================
# 5. BERANDA
# ============================================================

if halaman == "Beranda":
    st.markdown("""
    <div class="kost-hero">
        <div class="kost-eyebrow">YOUR NEXT CHAPTER STARTS HERE</div>
        <div class="kost-hero-title">Temukan kost yang<br>terasa seperti rumah.</div>
        <p class="kost-hero-copy">Bandingkan harga, jarak, luas kamar, dan fasilitas dalam satu tempat. Biar kamu bisa memilih kost dengan lebih mudah dan percaya diri.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("🏡 Total data kost", len(st.session_state.daftar_kost))
    col2.metric("💰 Batas budget", format_rupiah(st.session_state.kriteria["harga_maks"]))
    col3.metric("📍 Jarak maksimal", f'{st.session_state.kriteria["jarak_maks"]:g} km')

    st.markdown("<div class='kost-section-label'>MULAI DARI SINI</div>", unsafe_allow_html=True)
    st.markdown("## Cari tempat yang paling cocok buatmu")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with st.container(border=True):
            st.markdown("### 🧭 Cari & ranking kost")
            st.write("Lihat pilihan yang sesuai kriteria dan temukan kost dengan skor tertinggi.")
            st.caption("Urutkan pilihan berdasarkan skor kecocokan.")
    with c2:
        with st.container(border=True):
            st.markdown("### 🌿 Atur preferensimu")
            st.write("Sesuaikan budget, jarak, luas kamar, dan fasilitas yang wajib ada.")
            st.caption("Kamu yang menentukan prioritasnya.")

    st.markdown("## Semua kebutuhan kost, satu tempat")
    f1, f2, f3 = st.columns(3, gap="medium")
    with f1:
        with st.container(border=True):
            st.markdown("### 💸 Budget friendly")
            st.write("Cari pilihan sesuai batas harga bulananmu.")
    with f2:
        with st.container(border=True):
            st.markdown("### 🚶 Dekat kampus")
            st.write("Pertimbangkan jarak agar aktivitas harian lebih praktis.")
    with f3:
        with st.container(border=True):
            st.markdown("### ✨ Ranking transparan")
            st.write("Lihat rincian skor untuk membandingkan setiap pilihan.")

    st.divider()
    st.caption("KOST12 · Temukan ruang yang pas untuk cerita barumu.")

# ============================================================
# 6. TAMBAH DATA KOST
# ============================================================

elif halaman == "Tambah Data Kost":
    st.subheader("➕ Tambah Data Kost")
    st.write("Isi informasi kost di bawah ini, lalu tekan tombol **Simpan Data Kost**.")

    with st.form("form_tambah_kost", clear_on_submit=True):
        nama = st.text_input("Nama kost *")
        col1, col2, col3 = st.columns(3)

        with col1:
            harga = st.number_input(
                "Harga per bulan (Rp) *",
                min_value=0,
                value=1_000_000,
                step=50_000,
            )
        with col2:
            jarak = st.number_input(
                "Jarak dari kampus (km) *",
                min_value=0.0,
                value=1.0,
                step=0.1,
                format="%.1f",
            )
        with col3:
            luas = st.number_input(
                "Luas kamar (m²) *",
                min_value=0.0,
                value=12.0,
                step=1.0,
                format="%.1f",
            )

        st.markdown("#### Fasilitas kamar")
        f1, f2, f3 = st.columns(3)
        with f1:
            ac = st.checkbox("AC tersedia")
        with f2:
            kamar_mandi = st.checkbox("Kamar mandi dalam")
        with f3:
            furnished = st.checkbox("Full furnished")

        st.markdown("#### Fasilitas lingkungan")
        f4, f5, f6 = st.columns(3)
        with f4:
            parkir = st.checkbox("Tempat parkir")
        with f5:
            ruang_hijau = st.checkbox("Akses ruang hijau")
        with f6:
            transportasi = st.checkbox("Dekat transportasi umum")

        kamar_tersisa = st.number_input(
            "Jumlah kamar yang masih tersedia *",
            min_value=0,
            value=1,
            step=1,
        )

        simpan = st.form_submit_button("💾 Simpan Data Kost", use_container_width=True)

    if simpan:
        if not nama.strip():
            st.warning("Nama kost tidak boleh kosong.")
        else:
            kost_baru = {
                "nama": nama.strip(),
                "harga": float(harga),
                "jarak": float(jarak),
                "luas": float(luas),
                "ac": ac,
                "kamar_mandi": kamar_mandi,
                "furnished": furnished,
                "parkir": parkir,
                "ruang_hijau": ruang_hijau,
                "transportasi": transportasi,
                "kamar_tersisa": int(kamar_tersisa),
            }
            st.session_state.daftar_kost.append(kost_baru)
            st.success(f"Data kost **{nama.strip()}** berhasil ditambahkan!")
            st.caption("Buka halaman Cari dan Ranking Kost untuk melihat hasilnya.")

# ============================================================
# 7. LIHAT SELURUH DATA KOST
# ============================================================

elif halaman == "Lihat Seluruh Data":
    st.subheader("📋 Seluruh Data Kost")

    if len(st.session_state.daftar_kost) == 0:
        st.warning("Belum ada data yang diinput.")
        st.write("Buka halaman **Tambah Data Kost** untuk memasukkan data terlebih dahulu.")
    else:
        baris = []
        for nomor, kost in enumerate(st.session_state.daftar_kost, start=1):
            baris.append({
                "No.": nomor,
                "Nama Kost": kost["nama"],
                "Harga/Bulan": format_rupiah(kost["harga"]),
                "Jarak (km)": kost["jarak"],
                "Luas (m²)": kost["luas"],
                "AC": "Ya" if kost["ac"] else "Tidak",
                "Kamar mandi dalam": "Ya" if kost["kamar_mandi"] else "Tidak",
                "Full furnished": "Ya" if kost["furnished"] else "Tidak",
                "Parkir": "Ya" if kost["parkir"] else "Tidak",
                "Ruang hijau": "Ya" if kost["ruang_hijau"] else "Tidak",
                "Transportasi umum": "Ya" if kost["transportasi"] else "Tidak",
                "Kamar tersisa": kost["kamar_tersisa"],
            })

        st.dataframe(pd.DataFrame(baris), use_container_width=True, hide_index=True)

        st.download_button(
            "⬇️ Unduh data sebagai CSV",
            data=pd.DataFrame(baris).to_csv(index=False).encode("utf-8-sig"),
            file_name="data_kost.csv",
            mime="text/csv",
        )

        st.divider()
        with st.expander("Hapus data kost"):
            st.warning("Penghapusan ini tidak bisa dibatalkan.")
            nama_hapus = st.selectbox(
                "Pilih kost yang ingin dihapus:",
                options=list(range(len(st.session_state.daftar_kost))),
                format_func=lambda i: st.session_state.daftar_kost[i]["nama"],
            )
            if st.button("🗑️ Hapus kost terpilih"):
                kost_dihapus = st.session_state.daftar_kost.pop(nama_hapus)
                st.success(f"Data {kost_dihapus['nama']} berhasil dihapus.")
                st.rerun()

# ============================================================
# 8. UBAH KRITERIA PENCARIAN
# ============================================================

elif halaman == "Ubah Kriteria":
    st.subheader("⚙️ Ubah Kriteria Pencarian")
    st.write("Pilih batas yang kamu inginkan. Centang fasilitas jika fasilitas tersebut wajib tersedia.")

    kriteria_lama = st.session_state.kriteria

    with st.form("form_kriteria"):
        harga_maks = st.number_input(
            "Harga maksimal per bulan (Rp)",
            min_value=0,
            value=int(kriteria_lama["harga_maks"]),
            step=50_000,
        )
        jarak_maks = st.number_input(
            "Jarak maksimal dari kampus (km)",
            min_value=0.0,
            value=float(kriteria_lama["jarak_maks"]),
            step=0.5,
            format="%.1f",
        )
        luas_min = st.number_input(
            "Luas kamar minimal (m²)",
            min_value=0.0,
            value=float(kriteria_lama["luas_min"]),
            step=1.0,
            format="%.1f",
        )

        st.markdown("#### Fasilitas wajib")
        k1, k2, k3 = st.columns(3)
        with k1:
            wajib_ac = st.checkbox("AC wajib", value=kriteria_lama["ac"])
            wajib_mandi = st.checkbox(
                "Kamar mandi dalam wajib", value=kriteria_lama["kamar_mandi"]
            )
        with k2:
            wajib_furnished = st.checkbox(
                "Full furnished wajib", value=kriteria_lama["furnished"]
            )
            wajib_parkir = st.checkbox("Parkir wajib", value=kriteria_lama["parkir"])
        with k3:
            wajib_hijau = st.checkbox(
                "Ruang hijau wajib", value=kriteria_lama["ruang_hijau"]
            )
            wajib_transportasi = st.checkbox(
                "Transportasi umum wajib", value=kriteria_lama["transportasi"]
            )

        simpan_kriteria = st.form_submit_button(
            "Simpan Kriteria", use_container_width=True
        )

    if simpan_kriteria:
        st.session_state.kriteria = {
            "harga_maks": float(harga_maks),
            "jarak_maks": float(jarak_maks),
            "luas_min": float(luas_min),
            "ac": wajib_ac,
            "kamar_mandi": wajib_mandi,
            "furnished": wajib_furnished,
            "parkir": wajib_parkir,
            "ruang_hijau": wajib_hijau,
            "transportasi": wajib_transportasi,
        }
        st.success("Kriteria pencarian berhasil diperbarui!")

# ============================================================
# 9. CARI DAN RANKING KOST
# ============================================================

elif halaman == "Cari dan Ranking Kost":
    st.subheader("🔎 Hasil Pencarian dan Ranking Kost")

    if len(st.session_state.daftar_kost) == 0:
        st.warning("Belum ada data yang diinput.")
        st.write("Tambahkan data kost terlebih dahulu, lalu kembali ke halaman ini.")
    else:
        k = st.session_state.kriteria
        with st.expander("Lihat kriteria pencarian yang sedang digunakan"):
            st.write(f"**Harga maksimal:** {format_rupiah(k['harga_maks'])}")
            st.write(f"**Jarak maksimal:** {k['jarak_maks']:g} km")
            st.write(f"**Luas minimal:** {k['luas_min']:g} m²")
            fasilitas_label = {
                "ac": "AC",
                "kamar_mandi": "Kamar mandi dalam",
                "furnished": "Full furnished",
                "parkir": "Parkir",
                "ruang_hijau": "Akses ruang hijau",
                "transportasi": "Dekat transportasi umum",
            }
            wajib = [label for key, label in fasilitas_label.items() if k[key]]
            st.write("**Fasilitas wajib:** " + (", ".join(wajib) if wajib else "Tidak ada"))

        hasil = cari_kost()

        if len(hasil) == 0:
            st.warning("Tidak ada kost yang sesuai dengan kriteria.")
            st.write("Coba ubah kriteria atau tambahkan data kost.")
        else:
            st.success(f"Ditemukan {len(hasil)} kost yang sesuai.")
            for peringkat, item in enumerate(hasil, start=1):
                kost = item["kost"]
                skor = item["skor"]

                with st.container(border=True):
                    kiri, kanan = st.columns([3, 1])
                    with kiri:
                        st.markdown(f"### #{peringkat} — {kost['nama']}")
                        st.write(
                            f"**Harga:** {format_rupiah(kost['harga'])}/bulan  \n"
                            f"**Jarak:** {kost['jarak']:g} km  \n"
                            f"**Luas kamar:** {kost['luas']:g} m²  \n"
                            f"**Kamar tersisa:** {kost['kamar_tersisa']}"
                        )

                        fasilitas = [
                            ("AC", kost["ac"]),
                            ("Kamar mandi dalam", kost["kamar_mandi"]),
                            ("Full furnished", kost["furnished"]),
                            ("Parkir", kost["parkir"]),
                            ("Ruang hijau", kost["ruang_hijau"]),
                            ("Transportasi umum", kost["transportasi"]),
                        ]
                        tersedia = [nama for nama, ada in fasilitas if ada]
                        st.caption(
                            "Fasilitas tersedia: "
                            + (", ".join(tersedia) if tersedia else "Belum ada fasilitas yang dicentang")
                        )

                    with kanan:
                        st.metric("Total skor", f"{skor['total']} / 27")

                    with st.expander("Lihat rincian skor"):
                        st.write(f"Harga: {skor['harga']} × 3 = {skor['harga'] * 3}")
                        st.write(f"Jarak: {skor['jarak']} × 2 = {skor['jarak'] * 2}")
                        st.write(f"Luas: {skor['luas']} × 2 = {skor['luas'] * 2}")
                        st.write(f"Fasilitas kamar: {skor['fasilitas']} × 1")
                        st.write(f"Lingkungan: {skor['lingkungan']} × 1")
                        st.write(f"**Total: {skor['total']} / 27**")

# ============================================================
# 10. TUTORIAL
# ============================================================

elif halaman == "Tutorial":
    st.subheader("📘 Tutorial Penggunaan Website")

    st.markdown("""
    **Langkah 1 — Masukkan data kost**

    Buka halaman **Tambah Data Kost**. Isi nama, harga, jarak, luas, fasilitas, dan jumlah kamar yang tersedia, lalu tekan **Simpan Data Kost**.

    **Langkah 2 — Atur kriteria pencarian**

    Buka halaman **Ubah Kriteria** untuk menentukan harga maksimal, jarak maksimal, luas minimal, dan fasilitas yang wajib tersedia.

    **Langkah 3 — Cari dan ranking kost**

    Buka halaman **Cari dan Ranking Kost**. Website akan menyaring data sesuai kriteria, lalu mengurutkan kost berdasarkan skor total tertinggi.

    **Langkah 4 — Periksa seluruh data**

    Buka halaman **Lihat Seluruh Data** untuk memeriksa data kost yang telah dimasukkan atau mengunduhnya sebagai CSV.

    **Catatan penting**

    - Data disimpan di memori sesi aplikasi dan tidak dijamin tetap ada setelah sesi aplikasi berakhir atau aplikasi dimulai ulang.
    - Tombol unduh CSV dapat digunakan untuk menyimpan salinan data.
    - Skor total maksimum adalah 27, mengikuti rumus pada program awal.
    """)
