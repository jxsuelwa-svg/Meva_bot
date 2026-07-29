import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# ================= CONFIGURACIÓN =================
TELEGRAM_BOT_TOKEN = "8423978432:AAHAziHcphZasmLJ-iayp4iJ48ceM9y8Kts"  # <-- Tu Token integrado
SMS_ACTIVATE_API_KEY = "EAc7fAdece652bd7d539A5bb76707d7c"  # <-- Tu API Key integrada

# ID de Telegram del administrador autorizado
ADMIN_IDS = [7390841762]  # <-- Tu ID de administrador configurado

SERVICE_ID = 'wa'  # ID de WhatsApp en SMS-Activate

PAISES_IDS = {
    "colombia": "3",
    "el_salvador": "59",
    "nicaragua": "74",
    "mexico": "4",
    "argentina": "34",
    "peru": "2"
}
# =================================================

# ================= BASE DE DATOS (SQLite3) =================
def init_db():
    conn = sqlite3.connect("bot_balance.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0.0
        )
    """)
    conn.commit()
    conn.close()

def obtener_o_crear_usuario(user_id: int):
    conn = sqlite3.connect("bot_balance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM usuarios WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("INSERT INTO usuarios (user_id, balance) VALUES (?, ?)", (user_id, 0.0))
        conn.commit()
        balance = 0.0
    else:
        balance = row[0]
    conn.close()
    return balance

def actualizar_balance(user_id: int, monto: float):
    conn = sqlite3.connect("bot_balance.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET balance = balance + ? WHERE user_id = ?", (monto, user_id))
    conn.commit()
    conn.close()
# ==========================================================

def comprar_numero_pais(pais: str):
    country_id = PAISES_IDS.get(pais)
    if not country_id:
        return {"error": "País no válido"}
    
    url = f"https://api.sms-activate.ae/stubs/handler_api.php?api_key={SMS_ACTIVATE_API_KEY}&action=getNumber&service={SERVICE_ID}&country={country_id}"
    
    try:
        response = requests.get(url)
        texto = response.text
        if "ACCESS_NUMBER" in texto:
            partes = texto.split(":")
            return {"success": True, "activation_id": partes[1], "phone": partes[2]}
        else:
            return {"success": False, "error": texto}
    except Exception as e:
        return {"success": False, "error": str(e)}

def consultar_sms_api(activation_id: str):
    url = f"https://api.sms-activate.ae/stubs/handler_api.php?api_key={SMS_ACTIVATE_API_KEY}&action=getStatus&id={activation_id}"
    
    try:
        response = requests.get(url)
        texto = response.text
        if "STATUS_OK" in texto:
            return {"status": "received", "code": texto.split(":")[1]}
        elif "STATUS_WAIT_CODE" in texto:
            return {"status": "waiting"}
        else:
            return {"status": "error", "message": texto}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Comandos del Bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balance = obtener_o_crear_usuario(user_id)
    await update.message.reply_text(
        f"¡Bienvenido! Tu saldo interno es: `${balance:.2f}`\n\n"
        f"Usa /comprar para ver los países disponibles o compra directamente con `/comprar_[pais]` (ej: `/comprar_mexico`)."
    )

async def consultar_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balance = obtener_o_crear_usuario(user_id)
    await update.message.reply_text(f"💰 Tu saldo actual es de: **${balance:.2f}**", parse_mode="Markdown")

async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    paises_txt = "\n".join([f"• /{pais}" for pais in PAISES_IDS.keys()])
    await update.message.reply_text(f"Selecciona el país escribiendo su comando:\n{paises_txt}")

async def comprar_pais_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comando = update.message.text.replace("/", "").lower()
    pais = comando.replace("comprar_", "")
    
    if pais not in PAISES_IDS:
        await update.message.reply_text("País no encontrado.")
        return

    await update.message.reply_text(f"🔄 Solicitando número real para WhatsApp en {pais.capitalize()}...")
    
    resultado = comprar_numero_pais(pais)
    
    if resultado.get("success"):
        act_id = resultado["activation_id"]
        telefono = resultado["phone"]
        await update.message.reply_text(
            f"✅ **¡Número adquirido con éxito!**\n\n"
            f"📞 **Número:** `+{telefono}`\n"
            f"🆔 **ID de Activación:** `{act_id}`\n\n"
            f"Usa el comando `/revisar {act_id}` para verificar si ya llegó el código SMS.",
            parse_mode="Markdown"
        )
    else:
        error_msg = resultado.get("error", "Desconocido")
        await update.message.reply_text(f"❌ No se pudo procesar la compra. Motivo: `{error_msg}`")

async def revisar_sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Por favor, incluye el ID de activación. Ejemplo: `/revisar 12345678`")
        return
    
    act_id = context.args[0]
    await update.message.reply_text(f"⏳ Consultando estado para el ID: {act_id}...")
    
    estado = consultar_sms_api(act_id)
    
    if estado["status"] == "received":
        await update.message.reply_text(f"🎉 **¡Código recibido!**\n\nEl código de verificación es: `{estado['code']}`", parse_mode="Markdown")
    elif estado["status"] == "waiting":
        await update.message.reply_text(f"⏳ Todavía no llega el SMS. Vuelve a intentar en unos segundos con `/revisar {act_id}`.")
    else:
        await update.message.reply_text(f"⚠️ Estado / Error: `{estado['message']}`")

# Comando exclusivo de Administrador para recargar saldo a usuarios
async def dar_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ No tienes permisos para usar este comando.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Uso correcto para admin: `/darsaldo [ID_USUARIO] [MONTO]`", parse_mode="Markdown")
        return
    
    try:
        target_user_id = int(context.args[0])
        monto = float(context.args[1])
        
        obtener_o_crear_usuario(target_user_id)
        actualizar_balance(target_user_id, monto)
        
        await update.message.reply_text(f"✅ Se han acreditado `${monto:.2f}` al usuario `{target_user_id}` con éxito.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Error en los datos. Asegúrate de que el ID y el monto sean números válidos.")

def main():
    init_db()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Comandos generales y de usuario
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("saldo", consultar_saldo))
    app.add_handler(CommandHandler("comprar", comprar))
    
    for pais in PAISES_IDS.keys():
        app.add_handler(CommandHandler(f"comprar_{pais}", comprar_pais_handler))
        
    app.add_handler(CommandHandler("revisar", revisar_sms))
    
    # Comando de administración
    app.add_handler(CommandHandler("darsaldo", dar_saldo))
    
    print("Bot corriendo con base de datos SQLite y API conectada...")
    app.run_polling()

if __name__ == "__main__":
    main()
