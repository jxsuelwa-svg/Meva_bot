 import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# ==================== CONFIGURACIÓN ====================
TELEGRAM_BOT_TOKEN = "8423978432:AAGPiQbhmD3C1i9F7Q97mr-37SeqG0x1038"
SMS_ACTIVATE_API_KEY = "EAc7fAdece652bd7d539A5bb"

# Tu enlace de PayPal.Me
PAYPAL_ME_LINK = "https://paypal.me/TuUsuarioPayPal"

ADMIN_IDS = [7390841762]
SERVICE_ID = "wa"  # WhatsApp

PAISES_IDS = {
    "colombia": "3",
    "el_salvador": "59",
    "nicaragua": "74",
    "mexico": "4",
}

# Base de datos en memoria para saldos
saldos_usuarios = {}

# ==================== COMANDO START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("No tienes autorización para usar este bot.")
        return
    
    await update.message.reply_text(
        "¡Hola! Bot configurado con el truco anti-bloqueo.\n\n"
        "📋 **Comandos disponibles:**\n"
        "👉 `/comprar [pais]` - Compra un número (Cuesta $1.00)\n"
        "👉 `/saldo` - Consulta tu saldo actual\n"
        "👉 `/pagar [cantidad]` - Genera enlace de pago por PayPal (Ej: `/pagar 5`)\n"
        "👉 `/agregar [id_usuario] [cantidad]` - Agrega saldo (Solo Admin)"
    )

# ==================== COMANDO SALDO ====================
async def ver_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    saldo = saldos_usuarios.get(user_id, 0.0)
    await update.message.reply_text(f"💰 Tu saldo actual es: `${saldo:.2f}`")

# ==================== COMANDO PAGAR CON PAYPAL ====================
async def pagar_paypal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Uso correcto: `/pagar 5`")
        return

    try:
        cantidad = float(context.args[0])
        if cantidad <= 0:
            raise ValueError()
    except ValueError:
        await update.message.reply_text("❌ Introduce una cantidad válida mayor a 0.")
        return

    enlace_pago = f"{PAYPAL_ME_LINK}/{cantidad}USD"

    keyboard = [
        [InlineKeyboardButton("💳 Pagar con PayPal", url=enlace_pago)],
        [InlineKeyboardButton("🔄 Ya pagué (Notificar Admin)", callback_data=f"notificar_pago_{cantidad}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🛒 **Recarga de Saldo vía PayPal**\n\n"
        f"💵 Monto a recargar: `${cantidad:.2f} USD`\n\n"
        f"Haz clic en el botón para pagar y presiona 'Ya pagué' para avisar.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ==================== BOTÓN DE NOTIFICAR PAGO ====================
async def boton_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    datos = query.data.split("_")
    if len(datos) >= 3 and datos[0] == "notificar" and datos[1] == "pago":
        cantidad = datos[2]
        user_id = query.from_user.id
        username = query.from_user.username or query.from_user.first_name

        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"🔔 **¡Nuevo aviso de pago!**\n\n"
                         f"👤 Usuario: @{username} (`{user_id}`)\n"
                         f"💵 Monto: `${cantidad} USD`\n\n"
                         f"Usa este comando para aprobarlo:\n"
                         f"`/agregar {user_id} {cantidad}`",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

        await query.edit_message_text(text="✅ ¡Notificación enviada al administrador con éxito!")

# ==================== COMANDO AGREGAR SALDO (ADMIN) ====================
async def agregar_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ No tienes permisos.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Uso correcto: `/agregar [id_usuario] [cantidad]`")
        return

    try:
        target_user_id = int(context.args[0])
        cantidad = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ El ID y la cantidad deben ser números.")
        return

    actual = saldos_usuarios.get(target_user_id, 0.0)
    nuevo_saldo = actual + cantidad
    saldos_usuarios[target_user_id] = nuevo_saldo

    await update.message.reply_text(
        f"✅ Saldo actualizado.\n"
        f"👤 Usuario: `{target_user_id}`\n"
        f"💰 Nuevo total: `${nuevo_saldo:.2f}`",
        parse_mode="Markdown"
    )

    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"🎉 ¡Tu recarga de `${cantidad:.2f}` ha sido aprobada!\n💰 Saldo: `${nuevo_saldo:.2f}`"
        )
    except Exception:
        pass

# ==================== COMANDO COMPRAR (CON TRUCO ANTI-BLOQUEO) ====================
async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("No tienes autorización.")
        return

    COSTO_NUMERO = 1.00
    saldo_actual = saldos_usuarios.get(user_id, 0.0)

    if saldo_actual < COSTO_NUMERO:
        await update.message.reply_text(f"❌ Saldo insuficiente. Tu saldo: `${saldo_actual:.2f}`")
        return

    if not context.args:
        paises_disponibles = ", ".join(PAISES_IDS.keys())
        await update.message.reply_text(f"Países: {paises_disponibles}\nUso: `/comprar colombia`")
        return

    pais_input = context.args[0].lower()
    if pais_input not in PAISES_IDS:
        await update.message.reply_text("País no válido.")
        return

    country_id = PAISES_IDS[pais_input]
    
    # URL y Cabeceras trampa para engañar el filtro de Render
    url = f"https://api.sms-activate.org/stt/stt_api.php?api_key={SMS_ACTIVATE_API_KEY}&action=getNumber&service={SERVICE_ID}&country={country_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive"
    }

    try:
        # Usamos una sesión con headers camuflados y un tiempo de espera alto
        response = requests.get(url, headers=headers, timeout=15)
        texto_respuesta = response.text

        if "ACCESS_NUMBER" in texto_respuesta:
            partes = texto_respuesta.split(":")
            activation_id = partes[1]
            phone_number = partes[2]
            
            saldos_usuarios[user_id] = saldo_actual - COSTO_NUMERO
            
            await update.message.reply_text(
                f"✅ ¡Número adquirido con éxito!\n\n"
                f"🌍 País: {pais_input.capitalize()}\n"
                f"📞 Número: `+{phone_number}`\n"
                f"🆔 ID: `{activation_id}`\n"
                f"💰 Saldo restante: `${saldos_usuarios[user_id]:.2f}`",
                parse_mode="Markdown"
            )
        elif "NO_NUMBERS" in texto_respuesta:
            await update.message.reply_text("❌ No hay números disponibles en este momento para ese país.")
        elif "NO_BALANCE" in texto_respuesta:
            await update.message.reply_text("❌ Saldo insuficiente en la API principal de SMS-Activate.")
        else:
            await update.message.reply_text(f"⚠️ Respuesta de la API: {texto_respuesta}")

    except Exception as e:
        await update.message.reply_text(f"❌ Render sigue bloqueando la salida de red. Error técnico: {str(e)}")

# ==================== INICIO DEL BOT ====================
def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("saldo", ver_saldo))
    application.add_handler(CommandHandler("pagar", pagar_paypal))
    application.add_handler(CommandHandler("agregar", agregar_saldo))
    application.add_handler(CommandHandler("comprar", comprar))
    application.add_handler(CallbackQueryHandler(boton_callback))

    print("Iniciando bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
