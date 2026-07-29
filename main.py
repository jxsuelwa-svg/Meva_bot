import sqlite3
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ==================== CONFIGURACIÓN ====================
TELEGRAM_BOT_TOKEN = "8423978432:AAGPiQbhmD3C1i9F7Q97mr-37SeqG0x1038"

SMS_ACTIVATE_API_KEY = "EAc7fAdece652bd7d539A5bb"

# ID de Telegram del administrador autorizado
ADMIN_IDS = [7390841762]  # <-- Tu ID de administrador

SERVICE_ID = "wa"  # ID de WhatsApp en SMS-Activate

PAISES_IDS = {
    "colombia": "3",
    "el_salvador": "59",
    "nicaragua": "74",
    "mexico": "4",
}
