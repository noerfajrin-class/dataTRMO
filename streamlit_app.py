import streamlit as st
import serpapi
import pandas as pd
from io import BytesIO

# =========================================
# KONFIGURASI
# =========================================

st.set_page_config(
    page_title="Data Publikasi Dosen",
    page_icon="📚",
    layout="wide"
)

# =========================================
# JUDUL
# =========================================

st.title("📚 Data Publikasi Dosen ")

st.write(
    "Mengambil data publikasi dosen "
    "berdasarkan Google Scholar Author ID, by Noer Fajrin."
)

# =========================================
# INPUT AUTHOR ID
# =========================================

author_id = st.text_input(
    "Google Scholar Author ID",
    placeholder="Contoh: zecgBo0AAAAJ"
)

# =========================================
# TOMBOL CARI
# =========================================

if st.button(
    "🔍 Ambil Data Publikasi",
    type="primary"
):

    if not author_id:
        st.warning(
            "Silakan masukkan Google Scholar Author ID."
        )
        st.stop()

    # =====================================
    # SERPAPI
    # =====================================

    client = serpapi.Client(
        api_key=st.secrets["SERPAPI_KEY"]
    )

    with st.spinner(
        "Mengambil data Google Scholar..."
    ):

        results = client.search({
            "engine": "google_scholar_author",
            "author_id": author_id,
            "hl": "en",
            "num": 100
        })

    # =====================================
    # CEK ERROR
    # =====================================

    if "error" in results:

        st.error(
            f"Terjadi error: {results['error']}"
        )

        st.stop()

    # =====================================
    # PROFIL PENULIS
    # =====================================

    author = results.get(
        "author",
        {}
    )

    if author:

        st.subheader("👤 Profil Penulis")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                f"### {author.get('name', '-')}"
            )

            st.write(
                author.get(
                    "affiliations",
                    "-"
                )
            )

        with col2:

            cited_by = author.get(
                "cited_by",
                {}
            )

            citation_table = cited_by.get(
                "table",
                []
            )

            total_citations = "-"

            if citation_table:

                total_citations = (
                    citation_table[0]
                    .get("citations", {})
                    .get("all", "-")
                )

            st.metric(
                "Total Sitasi",
                total_citations
            )

    # =====================================
    # PUBLIKASI
    # =====================================

    articles = results.get(
        "articles",
        []
    )

    st.divider()

    st.subheader(
        f"📚 Publikasi ({len(articles)})"
    )

    data = []

    for article in articles:

        authors = article.get(
            "authors",
            ""
        )

        title = article.get(
            "title",
            ""
        )

        year = article.get(
            "year",
            ""
        )

        link = article.get(
            "link",
            ""
        )

        cited_by = article.get(
            "cited_by",
            {}
        )

        citation = cited_by.get(
            "value",
            0
        )

        publication = article.get(
            "publication",
            ""
        )

        data.append({
            "Nama Penulis": authors,
            "Judul": title,
            "Tahun": year,
            "Sitasi": citation,
            "Publikasi": publication,
            "Link": link
        })

    # =====================================
    # TABEL
    # =====================================

    if data:

        df = pd.DataFrame(data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,

            column_config={

                "Link": st.column_config.LinkColumn(
                    "Link Publikasi",
                    display_text="🔗 Buka"
                ),

                "Sitasi": st.column_config.NumberColumn(
                    "Sitasi",
                    format="%d"
                )

            }
        )

        # =================================
        # EXPORT EXCEL
        # =================================

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="Publikasi"
            )

        excel_data = output.getvalue()

        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name=f"publikasi_{author_id}.xlsx",
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            )
        )

    else:

        st.warning(
            "Tidak ditemukan publikasi."
        )