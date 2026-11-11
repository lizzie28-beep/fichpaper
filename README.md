# FichPaper

> Extraemos metodología, variables e idea principal de artículos académicos automáticamente, para que investigadores no lean cientos de abstracts a mano.

## 1. One-liner
FichPaper extrae metodología, variables dependientes e independientes e idea principal de artículos académicos mediante LLMs, para que investigadores y tesistas no pasen semanas clasificando literatura a mano.

## 2. Founder
Soy Lizbeth Huaman Malpartida, Asistente de Investigación en el Centro de Investigación de  la Universidad del Pacífico. Clasifiqué 
manualmente más de 2,000 artículos académicos y leí más de 800 abstracts para un proyecto de revisión sistemática. Conozco el problema desde adentro, ya que es un asunto recurrente que sucede con otros compañeros.

## 3. Problema
Investigadores, asistentes de investigación y tesistas pierden semanas clasificando artículos académicos a mano para revisiones sistemáticas. Identificar la metodología, las variables y el hallazgo principal de cada artículo requiere leer cientos de abstracts uno por uno. Es lento, costoso y propenso a errores.

Hoy se resuelve con trabajo manual en Excel, con equipos de 2 o más personas y semanas de dedicación.

Ver conversaciones con usuarios en `docs/research/`.

## 4. Solución e insight
FichPaper permite subir un CSV con títulos y abstracts y extrae automáticamente:
- Metodología (cuantitativa, cualitativa o mixta)
- Si es estudio de caso
- Variable dependiente
- Variables independientes
- Idea principal

**Insight:** el abstract contiene suficiente información para clasificar un artículo. No hace falta leer el paper completo.

## 5. Why now
Hace tres años los LLMs no tenían la capacidad de extracción estructurada confiable que tienen hoy. Con modelos como Qwen 3 vía Groq, el costo por artículo es menor a $0.001 y la velocidad es de segundos por paper.

## 6. Demo

**URL pública:** https://fichpaper-pvpryaplylz9wyt6fsodwy.streamlit.app/

**Cómo correrlo en local:**
```bash
git clone https://github.com/lizzie28-beep/fichpaper
cd fichpaper
pip install -r requirements.txt
cp .env.example .env  # agregar GROQ_API_KEY
streamlit run app.py
```

**Arquitectura:**
```
CSV (título + abstract)
        ↓
  Streamlit (frontend)
        ↓
  Groq API (qwen/qwen3.8-27b)
        ↓
  JSON estructurado
        ↓
  Tabla + descarga CSV
```

**Modelos y APIs:**
- Groq API con `qwen/qwen3.8-27b` — rápido, gratuito y con buena capacidad de extracción estructurada.

**Capturas:**

_Agregar 3 capturas de pantalla de la app funcionando._

## 7. Modelo de negocio
- **Quién paga:** centros de investigación, consultoras, tesistas de posgrado
- **Precio:** S/ 9/mes (plan individual, hasta 500 artículos) o S/ 49/mes (plan institucional, ilimitado)
- **Costo por usuario:** ~$0.001 por artículo procesado en tokens. 1,000 artículos = $1.

## 8. Herramientas del curso

| Herramienta | Sesión | Archivo |
|---|---|---|
| LLMs con salidas estructuradas | s08 | `app.py` |

**Por qué estas herramientas:**
- **LLMs con salidas estructuradas (s08):** permite extraer campos específicos en formato JSON de manera confiable, sin necesidad de parsear texto libre.

## 9. Qué hizo el agente
Claude Code generó:
- El archivo `app.py` completo con la lógica de extracción
- La integración con Groq API en reemplazo de la API de Anthropic
- El manejo de columnas en inglés y español (title/título, authors/autor, etc.)
- El sistema de detección y reporte de errores por fila
- La lógica de mapeo flexible de columnas del CSV
