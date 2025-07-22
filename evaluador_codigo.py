import web
import os
import requests
import json
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

# Configurar render de plantillas
render = web.template.render('templates')

class EvaluadorCodigo:
    def GET(self):
        return render.evaluador_codigo()

    def POST(self):
        form = web.input(codigo_html="")
        codigo = form.codigo_html.strip()

        if not codigo:
            return render.evaluador_codigo(resultado="Por favor escribe tu código antes de enviarlo.")

        # Obtener clave y modelo desde .env
        api_key = os.getenv("GROQ_API_KEY")
        modelo = os.getenv("GROQ_MODEL", "llama3-8b-8192")

        if not api_key:
            return render.evaluador_codigo(resultado="Falta la clave de API en el archivo .env (GROQ_API_KEY).")

        prompt = (
            "Evalúa el siguiente código HTML proporcionado por un estudiante. "
            "Califica de 1 a 10 y proporciona retroalimentación clara sobre "
            "qué hace bien, qué está mal y cómo puede mejorar.\n\nCódigo:\n" + codigo
        )

        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un evaluador experto en programación web."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            feedback = data["choices"][0]["message"]["content"]
            return render.evaluador_codigo(resultado=feedback, codigo_enviado=codigo)
        except Exception as e:
            return render.evaluador_codigo(resultado=f"Error al evaluar: {str(e)}")
