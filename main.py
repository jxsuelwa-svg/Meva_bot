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
    
    await update.message.reply_text(
        "¡Hola! Bot conectado correctamente.\n\n"
        "Comandos disponibles:\n"
        "👉 `/comprar [pais]` (Ejemplo: `/comprar colombia`)"
    )

# ==================== COMANDO COMPRAR ====================
async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("No tienes autorización para usar este bot.")
        return

    # Verificar si escribió el país
    if not context.args:
        paises_disponibles = ", ".join(PAISES_IDS.keys())
        await update.message.reply_text(
            f"Debes indicar un país.\nPaíses disponibles: {paises_disponibles}\n"
            f"Uso correcto: `/comprar colombia`"
        )
        return

    pais_input = context.args[0].lower()
    if pais_input not in PAISES_IDS:
        await update.message.reply_text("País no válido. Revisa los países disponibles con `/start`.")
        return

    country_id = PAISES_IDS[pais_input]

    # Petición a la API de SMS-Activate para obtener el número
    url = f"https://api.sms-activate.org/stt/stt_api.php?api_key={SMS_ACTIVATE_API_KEY}&action=getNumber&service={SERVICE_ID}&country={country_id}"
    
    try:
        response = requests.get(url)
        texto_respuesta = response.text

        if "ACCESS_NUMBER" in texto_respuesta:
            partes = texto_respuesta.split(":")
            activation_id = partes[1]
            phone_number = partes[2]
            
            await update.message.reply_text(
                f"✅ ¡Número adquirido con éxito!\n\n"
                f"🌍 País: {pais_input.capitalize()}\n"
                f"📞 Número: `+{phone_number}`\n"
                f"🆔 ID de activación: `{activation_id}`",
                parse_mode="Markdown"
            )
        elif "NO_NUMBERS" in texto_respuesta:
            await update.message.reply_text("❌ No hay números disponibles en este momento para ese país.")
        elif "NO_BALANCE" in texto_respuesta:
            await update.message.reply_text("❌ Saldo insuficiente en tu cuenta de SMS-Activate.")
        else:
            await update.message.reply_text(f"⚠️ Respuesta de la API: {texto_respuesta}")

    except Exception as e:
        await update.message.reply_text(f"❌ Ocurrió un error de conexión con la API: {str(e)}")

# ==================== INICIO DEL BOT ====================
def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Registrar comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("comprar", comprar))

    # Iniciar el bot
    print("Iniciando bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
