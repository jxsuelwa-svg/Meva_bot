import sqlite3
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ==================== CONFIGURACIÓN ====================
TELEGRAM_BOT_TOKEN = "8423978432:AAGPiQbhmD3C1i9F7Q97mr-37SeqG0x1038"
SMS_ACTIVATE_API_KEY = "EAc7fAdece652bd7d539A5bb"

# ID de Telegram del administrador autorizado
ADMIN_IDS = [7390841762]

SERVICE_ID = "wa"  # ID de WhatsApp en SMS-Activate

PAISES_IDS = {
    "colombia": "3",
    "el_salvador": "59",
    "nicaragua": "74",
    "mexico": "4",
}

# ==================== COMANDO START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("No tienes autorización para usar este bot.")
        return
    
    await update.message.reply_text("¡Hola! Bot conectado correctamente y listo para usar con SMS-Activate.")

# ==================== INICIO DEL BOT ====================
def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Registrar comandos
    application.add_handler(CommandHandler("start", start))

    # Iniciar el bucle para mantener el bot activo en Render
    print("Iniciando bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
