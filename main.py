import os
import logging
from dotenv import load_dotenv
import telebot
import anthropic

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Cargar variables de entorno
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    logging.error("Error: TELEGRAM_BOT_TOKEN no está definido en las variables de entorno.")
    exit(1)

if not ANTHROPIC_API_KEY:
    logging.error("Error: ANTHROPIC_API_KEY no está definido en las variables de entorno.")
    exit(1)

# Inicializar bot de Telegram
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
logging.info("Bot de Telegram inicializado.")

# Inicializar cliente de Anthropic
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
logging.info("Cliente de Anthropic inicializado.")

# Cargar SWAIP_BIBLE.md
SWAIP_BIBLE_PATH = "SWAIP_BIBLE.md"
try:
    with open(SWAIP_BIBLE_PATH, "r", encoding="utf-8") as f:
        SYSTEM_CONTENT = f.read().strip()
    logging.info(f"SWAIP_BIBLE.md cargado desde {SWAIP_BIBLE_PATH}")
except FileNotFoundError:
    logging.error(f"Error: {SWAIP_BIBLE_PATH} no encontrado.")
    exit(1)
except Exception as e:
    logging.error(f"Error al leer {SWAIP_BIBLE_PATH}: {e}")
    exit(1)

# Manejador de mensajes de Telegram
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_text = message.text
    logging.info(f"Mensaje recibido de {chat_id}: {user_text}")

    try:
        # Preparar mensajes para Anthropic
        messages = [
            {"role": "user", "content": user_text}
        ]

        # Llamar a la API de Anthropic
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620", # Usamos el mismo modelo que antes
            max_tokens=1024,
            system=SYSTEM_CONTENT,
            messages=messages,
        )
        anthropic_response = response.content[0].text.strip()
        logging.info(f"Respuesta de Anthropic: {anthropic_response}")

        # Enviar respuesta a Telegram
        bot.send_message(chat_id, anthropic_response)

    except Exception as e:
        logging.error(f"Error al procesar el mensaje para {chat_id}: {e}")
        bot.send_message(chat_id, "Lo siento, hubo un error al procesar tu solicitud.")

# Iniciar el bot
if __name__ == "__main__":
    logging.info("IonBot (Python) iniciado y esperando mensajes...")
    bot.polling(non_stop=True)
