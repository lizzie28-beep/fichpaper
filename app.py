import io
import json
import os
import re

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "qwen/qwen3.8-27b"
COLUMN_ALIASES = {
    "journal": ["journal"],
    "título": ["title", "título"],
    "autor": ["authors", "autor"],
    "año": ["year", "año"],
    "abstract": ["abstract", "resumen"],
    "doi": ["doi"],
}

EXTRACTION_COLUMNS = [
    "metodologia",
    "es_estudio_de_caso",
    "variable_dependiente",
    "variables_independientes",
    "idea_principal",
]

SYSTEM_PROMPT = """Eres un asistente de investigación que ficha artículos académicos.
Dado el título y el abstract de un paper, responde ÚNICAMENTE con un objeto JSON
válido (sin texto adicional, sin markdown, sin ```), con exactamente estas claves:

{
  "metodologia": "Cuantitativa" | "Cualitativa" | "Mixta",
  "es_estudio_de_caso": "Sí" | "No",
  "variable_dependiente": "<string, o 'No identificada' si no aplica>",
  "variables_independientes": ["<string>", ...],
  "idea_principal": "<una sola línea que resuma la idea principal del paper>"
}

Si el abstract no permite determinar algún campo con certeza, usa tu mejor
inferencia razonada en lugar de dejarlo vacío."""


@st.cache_data(ttl=3600)
def get_groq_models(_client):
    return sorted(m.id for m in _client.models.list().data)


def find_column(df, aliases):
    aliases_norm = {a.strip().lower() for a in aliases}
    for col in df.columns:
        if col.strip().lower() in aliases_norm:
            return col
    return None


def extract_json(text):
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


def fichar_paper(client, titulo, abstract):
    user_content = f"Título: {titulo}\n\nAbstract: {abstract}"
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=400,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )
    text = response.choices[0].message.content or ""
    data = extract_json(text)

    variables_ind = data.get("variables_independientes", [])
    if isinstance(variables_ind, list):
        variables_ind = "; ".join(str(v) for v in variables_ind)

    return {
        "metodologia": data.get("metodologia", ""),
        "es_estudio_de_caso": data.get("es_estudio_de_caso", ""),
        "variable_dependiente": data.get("variable_dependiente", ""),
        "variables_independientes": variables_ind,
        "idea_principal": data.get("idea_principal", ""),
    }


st.set_page_config(page_title="FichPaper", layout="wide")
st.title("FichPaper")
st.caption(
    "Sube un CSV de papers y extrae metodología, variables e idea principal con Groq."
)

if "GROQ_API_KEY" not in os.environ:
    st.error(
        "No se encontró GROQ_API_KEY. Define esta variable en un archivo .env "
        "en la raíz del proyecto (ver .env.example)."
    )
    st.stop()

client = Groq()

st.subheader("Modelos disponibles en Groq")
try:
    available_models = get_groq_models(client)
    st.write(available_models)
except Exception as e:
    st.warning(f"No se pudieron obtener los modelos de Groq: {e}")

uploaded_file = st.file_uploader("Archivo CSV", type=["csv"])

if "results_df" not in st.session_state:
    st.session_state.results_df = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"No se pudo leer el CSV: {e}")
        st.stop()

    column_map = {
        canonical: find_column(df, aliases)
        for canonical, aliases in COLUMN_ALIASES.items()
    }
    missing = [
        " / ".join(COLUMN_ALIASES[req])
        for req, col in column_map.items()
        if col is None
    ]
    if missing:
        st.error(f"Faltan columnas requeridas en el CSV: {', '.join(missing)}")
        st.stop()

    st.write(f"{len(df)} filas cargadas.")
    st.dataframe(df.head(), use_container_width=True)

    if st.button("Procesar con Groq", type="primary"):
        progress = st.progress(0.0, text="Procesando...")
        rows = []
        total = len(df)

        for i, (_, row) in enumerate(df.iterrows()):
            titulo = row[column_map["título"]]
            abstract = row[column_map["abstract"]]

            try:
                extracted = fichar_paper(client, titulo, abstract)
            except Exception as e:
                extracted = {col: f"ERROR: {e}" for col in EXTRACTION_COLUMNS}

            rows.append({**row.to_dict(), **extracted})
            progress.progress(
                (i + 1) / total, text=f"Procesando {i + 1}/{total}"
            )

        progress.empty()
        st.session_state.results_df = pd.DataFrame(rows)
        st.success("Procesamiento completo.")

if st.session_state.results_df is not None:
    st.subheader("Resultados")
    st.dataframe(st.session_state.results_df, use_container_width=True)

    csv_buffer = io.StringIO()
    st.session_state.results_df.to_csv(csv_buffer, index=False)
    st.download_button(
        "Descargar CSV",
        data=csv_buffer.getvalue(),
        file_name="fichpaper_resultados.csv",
        mime="text/csv",
    )
