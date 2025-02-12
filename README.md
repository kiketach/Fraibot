🤖 FraiBot

FraiBot es un asistente virtual diseñado para apoyar al equipo de Frailejon.Tech en tareas creativas, estratégicas y operativas. Desde la generación de contenido hasta el envío masivo de correos electrónicos, FraiBot está aquí para impulsar el crecimiento de tu comunidad y proyectos. 

🌟 Características principales:
- Asistencia inteligente: Usa Gemini AI para responder preguntas, generar ideas creativas y proporcionar soluciones innovadoras.

- Envío masivo de correos: Procesa archivos Excel o CSV para enviar correos personalizados a múltiples destinatarios.

- Generador de ideas para eventos: Proporciona ideas creativas para eventos relacionados con tecnología, streaming y análisis de datos.

- Generador de ideas para contenido audiovisual: Proporciona ideas creativas para generar contenido audisovisual incluyendo el guión por escenas.

Interfaz amigable: Interactúa fácilmente a través de comandos y botones en Telegram.

🛠 Tecnologías utilizadas
- Backend: Python
- APIs:
    Telegram Bot API
    Google Gemini API
    SendGrid API
    Despliegue: Render

- Herramientas adicionales:
    python-telegram-bot
    pandas
    dotenv

🚀 Instalación y configuración
-Requisitos previos
-Python 3.8 o superior
-Una cuenta de Telegram para crear un bot (BotFather)
-Claves API para:
    -Google Gemini
    -SendGrid

Pasos para ejecutar localmente
-Clona este repositorio:
    git clone https://github.com/tu-usuario/fraibot.git
    cd fraibot

-Instala las dependencias:
    pip install -r requirements.txt

-Configura las variables de entorno:

- Crea un archivo .env en la raíz del proyecto y agrega las siguientes variables:
    TELEGRAM_KEY=tu_clave_de_telegram
    API_KEY=tu_clave_de_gemini
    SENDGRID_API_KEY=tu_clave_de_sendgrid
    EMAIL_SENDER=correo_remitente@example.com

python Bot.py
📦 Estructura del proyecto
fraibot/
├── Bot.py               # Código principal del bot
├── requirements.txt     # Dependencias del proyecto
├── .env                 # Variables de entorno (no subir a GitHub)
├── README.md            # Documentación del proyecto
└── downloads/           # Carpeta para archivos temporales

🎯 Comandos disponibles
- /start: Inicia el bot y muestra las opciones disponibles.
- /ayuda: Muestra una lista de comandos y su descripción.
-Botón "Ideas para Eventos": Genera ideas creativas para eventos relacionados con tecnología y streaming.
- Sube un archivo Excel o CSV para enviar correos masivos.

📈 Ejemplo de uso
-Envío masivo de correos
    Prepara un archivo Excel o CSV con las siguientes columnas:
        correo: Dirección de correo electrónico del destinatario.
        nombre: Nombre del destinatario.
        mensaje: Mensaje personalizado.
        Sube el archivo al bot y espera a que los correos se envíen.

Generador de ideas para eventos
    Haz clic en el botón "💡 Ideas para Eventos".
    Recibe una idea creativa para tu próximo evento.
    Si no te gusta, haz clic en "🔄 Generar otra idea".

🤝 Contribuciones
¡Las contribuciones son bienvenidas! Si deseas mejorar FraiBot, sigue estos pasos:

Haz un fork del repositorio.
    Crea una nueva rama (git checkout -b feature/nueva-funcionalidad).
    Realiza tus cambios y confírmalos (git commit -m "Añadir nueva funcionalidad").
    Sube tus cambios (git push origin feature/nueva-funcionalidad).
    Abre un pull request.

📜 Licencia
Este proyecto está bajo la licencia MIT . Consulta el archivo LICENSE para más detalles.

📞 Contacto
Si tienes preguntas o sugerencias, no dudes en contactarme:

Correo: kiketachira@gmail.com
LinkedIn: https://www.linkedin.com/in/enrique-abril-contreras