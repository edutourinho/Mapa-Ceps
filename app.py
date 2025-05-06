import streamlit as st
import pandas as pd, numpy as np, colorsys
import folium
from shapely.geometry import Point, shape
from streamlit_folium import st_folium
from folium.plugins import Draw

# 1 ───────── Configuração visual TRT-1 (idem antes) ─────────
st.set_page_config(page_title="Mapa de Mandados por CEP", layout="wide")
st.markdown("""<style>
h1,h2,h3,h4{color:#0A3A6A;font-weight:600;}
div[data-testid="metric-container"]>label{color:#0A3A6A !important;font-weight:600;}
section[data-testid="stSidebar"]{background:#EFF1F3;border-right:3px solid #0A3A6A;}
</style>""",unsafe_allow_html=True)

st.image("static/logo_trt1_horizontal.png", width=360)
st.title("Mapa de Mandados por CEP")

# 2 ───────── Sidebar: upload + placeholders ─────────
with st.sidebar:
    st.header("📂 Dados de entrada")
    arquivo = st.file_uploader("Envie 'cep.csv' (cep, ocorrencias, lat, lon, oj)", type="csv")
    st.divider()
    st.header("📊 Totais por OJ")
    totais_box = st.empty()
    st.divider()
    st.header("📍 Área desenhada")
    resultado_box = st.empty()

# 3 ───────── Corpo principal ─────────
if arquivo:
    df = pd.read_csv(arquivo)
    df["cep"] = df["cep"].astype(str).str.zfill(8)
    df.dropna(subset=["lat", "lon"], inplace=True)
    if "oj" not in df.columns:          # garantia
        df["oj"] = "Sem OJ"
    st.success(f"{len(df)} CEPs carregados.")

    # 3.1  Paleta de cores contrastantes  ───────────────────
    def hsv_palette(n, s=0.85, v=0.8):
        """Gera n cores HSV saturadas (evita tons claros/cinza)."""
        return [
            "#{:02x}{:02x}{:02x}".format(
                *[int(c*255) for c in colorsys.hsv_to_rgb(i/n, s, v)]
            )
            for i in range(n)
        ]

    unique_ojs = df["oj"].fillna("Sem OJ").unique()
    palette     = hsv_palette(len(unique_ojs))
    oj_color    = dict(zip(unique_ojs, palette))

    # 3.2  Totais globais por OJ  (sidebar)  ────────────────
    totais_df = (
        df.groupby("oj", as_index=False)["ocorrencias"]
          .sum()
          .rename(columns={"oj":"OJ", "ocorrencias":"Ocorrências"})
          .sort_values("Ocorrências", ascending=False)
    )
    with totais_box:
        st.dataframe(
            totais_df,
            hide_index=True,
            use_container_width=True,
            height=min(400, 35 + 28*len(totais_df))
        )

    # 3.3  Mapa + pontos  ───────────────────────────────────
    mapa = folium.Map(location=[-22.9, -43.2], zoom_start=11)

    for _, r in df.iterrows():
        cor = oj_color.get(r["oj"], "#0A3A6A")
        folium.CircleMarker(
            [r["lat"], r["lon"]],
            radius=5 + r["ocorrencias"]*0.3,
            color=cor, fill_color=cor, fill=True, fill_opacity=0.7,
            popup=f"<b>OJ:</b> {r['oj']}<br><b>CEP:</b> {r['cep']}<br><b>Ocorrências:</b> {r['ocorrencias']}"
        ).add_to(mapa)

    # 3.4  Legendinha  ──────────────────────────────────────
    legenda = "<div style='position:fixed;bottom:30px;left:30px;z-index:9999;" \
              "background:rgba(255,255,255,0.9);padding:8px;border:1px solid #999;border-radius:4px;'>"
    legenda += "<b>Legenda – OJ</b><br>"
    for oj, cor in oj_color.items():
        legenda += f"<span style='display:inline-block;width:12px;height:12px;background:{cor};margin-right:6px;'></span>{oj}<br>"
    legenda += "</div>"
    mapa.get_root().html.add_child(folium.Element(legenda))

    # 3.5  Ferramenta de desenho e exibição  ────────────────
    Draw(export=False,
         draw_options=dict(rectangle=True, polygon=True, polyline=False,
                           marker=False, circle=False, circlemarker=False),
         edit_options={"edit":True}).add_to(mapa)

    output = st_folium(mapa, use_container_width=True, height=800,
                       returned_objects=["last_active_drawing"])

    # 3.6  Processo seleção  ────────────────────────────────
    # 3.6  Processa a área desenhada  ──────────────────────────
    if (output and output.get("last_active_drawing")
            and output["last_active_drawing"].get("geometry")):
        geo = output["last_active_drawing"]["geometry"]

    # Usa apenas polígonos (retângulo/polígono) por enquanto
        if geo["type"] == "Polygon":
            pol = shape(geo)
            inside = df.apply(
            lambda r: pol.contains(Point(r["lon"], r["lat"])), axis=1
            )

            filtrado = df.loc[inside].copy()
            qtd      = int(filtrado.shape[0])
            total    = int(filtrado["ocorrencias"].sum())

            with resultado_box.container():
                if qtd:
                    col1, col2 = st.columns(2)
                    col1.metric("CEPs na área", qtd)
                    col2.metric("Ocorrências", total)

                # ── Botão para exportar CSV ──
                    csv_bytes = filtrado.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Baixar CSV dos CEPs na área",
                        data=csv_bytes,
                        file_name="ceps_area_selecionada.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("Nenhum CEP dentro da área selecionada.")
