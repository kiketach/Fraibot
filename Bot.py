import os
import pandas as pd
import google.generativeai as genai
import sendgrid
from sendgrid.helpers.mail import Mail
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
import logging
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Cargar variables de entorno
load_dotenv()

# Configuración inicial
TELEGRAM_TOKEN = os.getenv("TELEGRAM_KEY")
GEMINI_API_KEY = os.getenv("API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_SENDER = os.getenv("SENDER_EMAIL")
PORT = int(os.getenv("PORT", 10000))  # Puerto para Render

# Configurar API de Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Diccionario para almacenar contexto de conversación por usuario
user_conversations = {}

# Configuración de logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")

# Servidor HTTP para mantener el bot en línea
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

# Iniciar servidor HTTP en segundo plano
def run_keep_alive_server():
    server = HTTPServer(('0.0.0.0', PORT), KeepAliveHandler)
    server.serve_forever()

# Comando /start
async def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("💡 Ideas para Eventos", callback_data="ideas_eventos")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 ¡Hola! Soy FraiBot. ¿En qué puedo ayudarte?", reply_markup=reply_markup)

# Manejador de botones interactivos
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    if query.data == "ideas_eventos":
        response = model.generate_content("Genera una idea para un evento de tecnología.")
        idea = response.text if response.text else "Lo siento, no pude generar una idea en este momento."
        
        keyboard = [[InlineKeyboardButton("🔄 Generar otra idea", callback_data="ideas_eventos")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"🌟 Aquí tienes una idea para tu evento:
\n{idea}", reply_markup=reply_markup)

# Responder mensajes de texto
async def recibir_mensaje(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    user_message = update.message.text
    user_conversations.setdefault(user_id, deque(maxlen=5)).append(f"Usuario: {user_message}")
    conversation_history = "\n".join(user_conversations[user_id])
    response = model.generate_content(f"{conversation_history}\n\nFraiBot:")
    bot_reply = response.text if response.text else "Lo siento, no pude generar una respuesta."
    user_conversations[user_id].append(f"FraiBot: {bot_reply}")
    await update.message.reply_text(bot_reply)

# Procesar archivos CSV o Excel
async def recibir_archivo(update: Update, context: CallbackContext):
    document = update.message.document
    file_path = f"downloads/{document.file_name}"
    os.makedirs("downloads", exist_ok=True)
    new_file = await context.bot.get_file(document.file_id)
    await new_file.download_to_drive(file_path)
    df = pd.read_excel(file_path) if document.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" else pd.read_csv(file_path)
    if not {'correo', 'nombre', 'mensaje'}.issubset(df.columns):
        return await update.message.reply_text("El archivo debe tener las columnas: correo, nombre y mensaje.")
    
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    with ThreadPoolExecutor(max_workers=10) as executor:
        for _, row in df.iterrows():
            executor.submit(send_email, sg, row["correo"], row["nombre"], row["mensaje"])
    await update.message.reply_text("📧 Correos enviados exitosamente!")

# Enviar correos con SendGrid
def send_email(sg, email, nombre, mensaje):
    mail = Mail(from_email=EMAIL_SENDER, to_emails=email, subject="Mensaje de Frailejon.Tech", plain_text_content=f"Hola {nombre},\n\n{mensaje}\n\nSaludos,")
    try:
        sg.send(mail)
    except Exception as e:
        logging.error(f"Error al enviar correo a {email}: {str(e)}")

# Función principal
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_mensaje))
    app.add_handler(MessageHandler(filters.Document.MimeType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") | filters.Document.MimeType("text/csv"), recibir_archivo))
    
    threading.Thread(target=run_keep_alive_server, daemon=True).start()
    print("🤖 FraiBot está corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()
