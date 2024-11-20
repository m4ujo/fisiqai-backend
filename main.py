import os, json
from fastapi import FastAPI
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse

class Question(BaseModel):
  text: str

load_dotenv()
app = FastAPI()

origins = [
  "https://fisiqai-ucsur.vercel.app/",
  "fisiqai-ucsur.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_api_data(prompt: str, model):
  response = model.generate_content(prompt) 
  return response.text

@app.get("/generate_questions/{topic}")
async def generate_questions(topic: str):
  prompt = f"Genera una lista de 5 preguntas de fisica a nivel UNIVERSITARIO unicamente sobre el tema {topic}, no incluyas otras temas de fisica." + """  
  Eres un profesor de física universitario asi que no pueden haber errores en las preguntas y sus respuestas correctas.
  La respuesta debe estar en formato JSON y el enconding debe ser UTF-8.

  Cada pregunta debe tener 4 opciones de respuesta y solo una de ellas puede ser la correcta. Necesito que también me des la opción correcta.
  
  Ejemplo:
  [
    {
      "question": pregunta,
      "options": 4 opciones (evita a toda costa el formato LATEX),
      "answer": respuesta correcta,
    },
    # ... resto del JSON
  ]

  Output:
  """

  try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
      model_name="gemini-1.5-pro",
      generation_config={"response_mime_type": "application/json"}
    )
    questions = json.loads(get_api_data(prompt, model))
    return {"questions": questions} 
  except Exception as e:
    return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/generate_resolution", response_class=PlainTextResponse)
async def get_resolution(question: Question):
  prompt = f"""Puedes darme la resolución del siguiente problema: {question.text}. Toda la respuesta en formato Markdown y si usas LATEX enciérralo entre $$, no uses '\'.Necesito que lo representes como una lista de pasos y coloques como título. Solo devuelve texto, nada en formato JSON.

  Utiliza el siguiente formato de ejemplo para toda respuesta que vayas a dar:

  # Resolución

  **Datos del problema:**
  Aqui necesito que en base al problema me des los datos que nos van a ayudar a resolverlo.

  <br />

  **Paso a paso:**
  - Paso 1: contenido de paso
  - Paso 2: contenido de paso
  - Paso 3: contenido de paso
  """

  try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
      model_name="gemini-1.5-pro"
    )
    data = get_api_data(prompt, model)
    return data
  except Exception as e:
    return JSONResponse(content={"error": str(e)}, status_code=500)