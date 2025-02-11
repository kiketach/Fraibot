import os
import pandas as pd
import google.generativeai as genai
import sendgrid
from sendgrid.helpers.mail import Mail
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer

# Cargar variables de entorno
load_dotenv()

# Configuración inicial
TELEGRAM_TOKEN = os.getenv("TELEGRAM_KEY")
GEMINI_API_KEY = os.getenv("API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_SENDER = os.getenv("SENDER_EMAIL")

# Configurar API de Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Contexto del bot
CONTEXT = """
Eres un asistente virtual llamado Frai, diseñado para ayudar al equipo de Frailejon.Tech en tareas creativas, estratégicas y operativas. Tu misión es apoyar en la generación de contenido, planificación de estrategias, diseño de logotipos, establecimiento de metas y cualquier otra tarea que impulse el crecimiento de Frailejon.Tech.
Frailejon.Tech es una plataforma que empodera a analistas e ingenieros de datos a través de formación de calidad, mentoría personalizada y herramientas innovadoras. Su misión es fomentar el crecimiento profesional en el ámbito de la tecnología y el análisis de datos.
Valores de Frailejon.Tech:
1. Crecimiento Continuo.
2. Colaboración.
3. Innovación.
4. Empoderamiento.
5. Inclusión.
Tu personalidad es profesional, innovadora y motivadora. Responde de manera clara y útil, siempre alineado con los valores y objetivos de Frailejon.Tech.
"""

# Configurar logging (reducir logs para no sobrecargar la terminal)
logging.basicConfig(
    level=logging.WARNING,  # Solo mostrar advertencias o errores
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log")]  # Guardar logs en un archivo
)

# Desactivar logs de httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

# Función para generar ideas para eventos
def generar_idea_evento():
    prompt = """
    Genera una idea creativa para un evento de streaming relacionado con tecnología y análisis de datos. 
    La idea debe incluir:
    - Un tema principal
    - Actividades sugeridas
   """
    response = model.generate_content(CONTEXT + "\n\n" + prompt)
    return response.text if response.text else "Lo siento, no pude generar una idea en este momento."

# Comando /start
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("💡 Ideas para Eventos", callback_data="ideas_eventos")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 ¡Hola! Soy FraiBot. ¿En qué puedo ayudarte? Usa el botón de abajo para obtener ideas para eventos.",
        reply_markup=reply_markup
    )

# Manejador de botones interactivos
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "ideas_eventos":
        idea = generar_idea_evento()
        keyboard = [
            [InlineKeyboardButton("🔄 Generar otra idea", callback_data="ideas_eventos")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"🌟 Aquí tienes una idea para tu evento:\n\n{idea}",
            reply_markup=reply_markup
        )

# Respuesta a mensajes de texto
async def recibir_mensaje(update: Update, context: CallbackContext):
    try:
        user_message = update.message.text
        full_prompt = CONTEXT + "\n\nPregunta del usuario: " + user_message
        response = model.generate_content(full_prompt)
        bot_reply = response.text if response.text else "Lo siento, no pude generar una respuesta."
        await update.message.reply_text(bot_reply)
    except Exception as e:
        logging.error(f"Error al procesar mensaje: {str(e)}")
        await update.message.reply_text("Ocurrió un error al procesar tu solicitud. Por favor, inténtalo de nuevo.")

# Procesar archivos Excel o CSV
async def recibir_archivo(update: Update, context: CallbackContext):
    try:
        document = update.message.document
        file_path = f"downloads/{document.file_name}"
        os.makedirs("downloads", exist_ok=True)
        new_file = await context.bot.get_file(document.file_id)
        await new_file.download_to_drive(file_path)

        # Leer el archivo según su tipo
        if document.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(file_path)
        elif document.mime_type == "text/csv":
            df = pd.read_csv(file_path)
        else:
            await update.message.reply_text("Formato de archivo no soportado. Sube un archivo Excel (.xlsx) o CSV.")
            return

        # Validar columnas necesarias
        if "correo" not in df.columns or "nombre" not in df.columns or "mensaje" not in df.columns:
            await update.message.reply_text("El archivo debe tener las columnas: correo, nombre y mensaje.")
            return

        # Enviar correos
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        with ThreadPoolExecutor(max_workers=10) as executor:
            for _, row in df.iterrows():
                executor.submit(send_email, sg, row["correo"], row["nombre"], row["mensaje"])

        await update.message.reply_text("📧 Correos enviados exitosamente!")
    except Exception as e:
        logging.error(f"Error al procesar archivo: {str(e)}")
        await update.message.reply_text("Ocurrió un error al procesar el archivo. Por favor, inténtalo de nuevo.")

# Función para enviar correos
def send_email(sg, email, nombre, mensaje):
    email_content = f"Hola {nombre},\n\n{mensaje}\n\nSaludos,\nFrailejon.Tech"
    mail = Mail(from_email=EMAIL_SENDER, to_emails=email, subject="Mensaje de Frailejon.Tech", plain_text_content=email_content)
    try:
        response = sg.send(mail)
        logging.info(f"Correo enviado a {email}: {response.status_code}")
    except Exception as e:
        logging.error(f"Error al enviar correo a {email}: {str(e)}")

# Función principal
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_mensaje))
    app.add_handler(MessageHandler(filters.Document.MimeType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") | filters.Document.MimeType("text/csv"), recibir_archivo))
    
    print("🤖 FraiBot está corriendo...")
    app.run_polling()
    
# Función para iniciar un servidor HTTP básico
def run_dummy_server():
    class DummyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

    server = HTTPServer(('0.0.0.0', 10000), DummyHandler)  # Puerto 10000
    server.serve_forever()

# Inicia el servidor HTTP en segundo plano
import threading
threading.Thread(target=run_dummy_server, daemon=True).start()

if __name__ == "__main__":
    main()