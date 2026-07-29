import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# ==================== CONFIGURACIÓN ====================
TELEGRAM_BOT_TOKEN = "8423978432:AAGPiQbhmD3C1i9F7Q97mr-37SeqG0x1038"
PAYPAL_ME_LINK = "https://paypal.me/TuUsuarioPayPal"

# Tu ID de administrador
ADMIN_IDS = [7390841762]

# Catálogo exacto basado en tus capturas
CATALOGO = {
    "android": {
        "nombre": "🤖 PANEL STORE — 🤖 Android",
        "productos": {
            "drip_client": {
                "nombre": "DRIP CLIENT MOD ✅ ( BEST SELLER ✨ )",
                "planes": {
                    "1d": {"tiempo": "1 Day", "precio": 93},
                    "3d": {"tiempo": "3 Days", "precio": 176},
                    "7d": {"tiempo": "7 Days", "precio": 342},
                    "15d": {"tiempo": "15 Days", "precio": 588},
                    "30d": {"tiempo": "30 Days", "precio": 882}
                }
            },
            "prime_hook": {
                "nombre": "PRIME HOOK",
                "planes": {
                    "1d": {"tiempo": "1 Day", "precio": 74},
                    "3d": {"tiempo": "3 Days", "precio": 166},
                    "7d": {"tiempo": "7 Days", "sold_out": True},
                    "14d": {"tiempo": "14 Days", "precio": 636}
                }
            },
            "proxy_server": {
                "nombre": "PROXY SERVER [DR-CL]",
                "planes": {
                    "1d": {"tiempo": "1 Day", "sold_out": True},
                    "3d": {"tiempo": "3 Days", "sold_out": True},
                    "7d": {"tiempo": "7 Days", "precio": 342},
                    "30d": {"tiempo": "30 Days", "sold_out": True}
                }
            }
        }
    },
    "iphone": {
        "nombre": "🍏 PANEL STORE — 🍏 iPhone",
        "productos": {
            "aimsilent_iphone": {
                "nombre": "AIMSILENT EXE (STREAMER)",
                "planes": {
                    "7d": {"tiempo": "7 Days", "sold_out": True},
                    "15d": {"tiempo": "15 Days", "precio": 587},
                    "30d": {"tiempo": "30 Days", "precio": 979}
                }
            },
            "basic_iphone": {
                "nombre": "BASIC (STREAMPROOF + SAFE )",
                "planes": {
                    "7d": {"tiempo": "7 Days", "sold_out": True},
                    "15d": {"tiempo": "15 Days", "precio": 587},
                    "30d": {"tiempo": "30 Days", "precio": 979}
                }
            }
        }
    }
}

saldos_usuarios = {}
historial_keys = {}

# ==================== MENÚ PRINCIPAL ====================
async def mostrar_menu_principal(update_or_query, context: ContextTypes.DEFAULT_TYPE, user_id=None, user_name="Usuario"):
    if not user_id and hasattr(update_or_query, "effective_user"):
        user_id = update_or_query.effective_user.id
    elif not user_id and hasattr(update_or_query, "from_user"):
        user_id = update_or_query.from_user.id

    saldo = saldos_usuarios.get(user_id, 0.0)

    texto = (
        f"🎉 **Hola {user_name}, Welcome Back!!**\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"▫️ **PIN de cliente: N{user_id}**\n"
        f"💰 **Tu Saldo Actual: ₹{saldo:.2f}**\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"💡 *Para simular una compra rápida por comando usa:* `/comprar`"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛒 Shop Now", callback_data="menu_shop")],
        [
            InlineKeyboardButton("🔑 My Orders", callback_data="menu_orders"),
            InlineKeyboardButton("👤 Profile", callback_data="menu_profile")
        ],
        [
            InlineKeyboardButton("💳 Pay Proof / Recargar", callback_data="menu_recargar")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update_or_query, "message") and update_or_query.message:
        await update_or_query.message.reply_text(texto, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        try:
            await update_or_query.edit_message_text(text=texto, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception:
            await update_or_query.message.reply_text(texto, reply_markup=reply_markup, parse_mode="Markdown")

# ==================== COMANDO START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await mostrar_menu_principal(update, context, user.id, user.first_name)

# ==================== COMANDO PARA SIMULAR COMPRA DIRECTA ====================
async def cmd_comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para simular una compra directa y generar la Key sin errores de carga"""
    user_id = update.effective_user.id
    
    # Ejemplo por defecto: Drip Client Mod - Plan 1 Día (₹93)
    cat_id = "android"
    prod_key = "drip_client"
    plan_key = "1d"
    
    prod_info = CATALOGO[cat_id]["productos"][prod_key]
    plan_info = prod_info["planes"][plan_key]
    precio = plan_info["precio"]
    nombre_producto = prod_info["nombre"]
    tiempo_plan = plan_info["tiempo"]

    saldo_actual = saldos_usuarios.get(user_id, 0.0)

    if saldo_actual < precio:
        await update.message.reply_text(
            f"❌ **Saldo insuficiente!**\n\n"
            f"Producto: {nombre_producto} ({tiempo_plan})\n"
            f"Precio: `₹{precio}`\n"
            f"Tu Saldo: `₹{saldo_actual}`\n\n"
            f"Usa el menú o pídele al admin saldo con `/agregar {user_id} 500`",
            parse_mode="Markdown"
        )
        return

    # Descontar saldo y generar Key
    saldos_usuarios[user_id] = saldo_actual - precio
    nueva_key = f"PANEL-{str(uuid.uuid4()).upper()[:16]}"

    if user_id not in historial_keys:
        historial_keys[user_id] = []
    historial_keys[user_id].append({"producto": nombre_producto, "plan": tiempo_plan, "key": nueva_key})

    await update.message.reply_text(
        f"✅ **¡Compra simulada con éxito!**\n\n"
        f"📦 Producto: {nombre_producto}\n"
        f"⏱ Plan: {tiempo_plan}\n"
        f"💵 Precio pagado: `₹{precio}`\n"
        f"🔑 **Key Generada:** `{nueva_key}`\n\n"
        f"💰 Saldo restante: `₹{saldos_usuarios[user_id]:.2f}`",
        parse_mode="Markdown"
    )

# ==================== MANEJADOR DE BOTONES ====================
async def boton_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user_name = query.from_user.username or query.from_user.first_name

    if data == "menu_inicio":
        await mostrar_menu_principal(query, context, user_id, query.from_user.first_name)

    elif data == "menu_profile":
        saldo = saldos_usuarios.get(user_id, 0.0)
        keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_inicio")]]
        await query.edit_message_text(
            text=f"👤 **Profile**\n\n▫️ PIN de cliente: `N{user_id}`\n👤 Name: {user_name}\n💰 Balance: **₹{saldo:.2f}**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data == "menu_shop":
        keyboard = [
            [InlineKeyboardButton("🤖 Android", callback_data="cat_android")],
            [InlineKeyboardButton("🍏 iPhone", callback_data="cat_iphone")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_inicio")]
        ]
        await query.edit_message_text(
            text="🛒 **PANEL STORE — SHOP**\n\n🔥 Choose your device category:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("cat_"):
        cat_id = data.split("_")[1]
        cat_data = CATALOGO[cat_id]
        keyboard = []
        for prod_key, prod_info in cat_data["productos"].items():
            keyboard.append([InlineKeyboardButton(prod_info["nombre"], callback_data=f"prod_{cat_id}_{prod_key}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back to Shop", callback_data="menu_shop")])

        await query.edit_message_text(
            text=f"📦 **{cat_data['nombre']}**\n\nChoose a product ⬇️",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("prod_"):
        partes = data.split("_")
        cat_id = partes[1]
        prod_key = partes[2]
        prod_info = CATALOGO[cat_id]["productos"][prod_key]

        keyboard = []
        for plan_key, plan_val in prod_info["planes"].items():
            if plan_val.get("sold_out"):
                btn_text = f"⏱ {plan_val['tiempo']} — Sold Out"
                cb_data = "sold_out_alert"
            else:
                btn_text = f"⏱ {plan_val['tiempo']} — ₹{plan_val['precio']}"
                cb_data = f"sim_buy_{cat_id}_{prod_key}_{plan_key}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=cb_data)])
        
        keyboard.append([InlineKeyboardButton("⬅️ Back to Shop", callback_data=f"cat_{cat_id}")])

        await query.edit_message_text(
            text=f"📦 **{prod_info['nombre']}**\n\n"
                 f"📥 *Extra 2% discount applied*\n"
                 f"Choose a plan ⬇️",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data == "sold_out_alert":
        await query.answer("❌ This plan is currently Sold Out!", show_alert=True)

    elif data.startswith("sim_buy_"):
        partes = data.split("_")
        cat_id, prod_key, plan_key = partes[2], partes[3], partes[4]
        prod_info = CATALOGO[cat_id]["productos"][prod_key]
        plan_info = prod_info["planes"][plan_key]
        precio = plan_info["precio"]
        
        keyboard = [
            [InlineKeyboardButton("✅ Confirm & Buy", callback_data=f"exec_buy_{cat_id}_{prod_key}_{plan_key}")],
            [InlineKeyboardButton("❌ Cancel", callback_data=f"prod_{cat_id}_{prod_key}")]
        ]
        await query.edit_message_text(
            text=f"🛒 **Confirm Purchase**\n\n"
                 f"📦 Product: **{prod_info['nombre']}**\n"
                 f"⏱ Plan: **{plan_info['tiempo']}**\n"
                 f"💵 Price: **₹{precio}**\n\n"
                 f"Do you want to proceed?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("exec_buy_"):
        partes = data.split("_")
        cat_id, prod_key, plan_key = partes[2], partes[3], partes[4]
        prod_info = CATALOGO[cat_id]["productos"][prod_key]
        plan_info = prod_info["planes"][plan_key]
        precio = plan_info["precio"]
        nombre_producto = prod_info["nombre"]
        tiempo_plan = plan_info["tiempo"]

        saldo_actual = saldos_usuarios.get(user_id, 0.0)

        if saldo_actual < precio:
            keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_inicio")]]
            await query.edit_message_text(
                text=f"❌ **Insufficient Balance!** Required: ₹{precio}, Your Balance: ₹{saldo_actual}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        saldos_usuarios[user_id] = saldo_actual - precio
        nueva_key = f"PANEL-{str(uuid.uuid4()).upper()[:16]}"

        if user_id not in historial_keys:
            historial_keys[user_id] = []
        historial_keys[user_id].append({"producto": nombre_producto, "plan": tiempo_plan, "key": nueva_key})

        keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_inicio")]]
        await query.edit_message_text(
            text=f"✅ **Key Generated Successfully!**\n\n"
                 f"📦 Product: {nombre_producto}\n"
                 f"⏱ Plan: {tiempo_plan}\n"
                 f"🔑 Key: `{nueva_key}`\n\n"
                 f"💰 Remaining Balance: `₹{saldos_usuarios[user_id]:.2f}`",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data == "menu_recargar":
        keyboard = [
            [InlineKeyboardButton("💵 Top up ₹500", callback_data="pay_500")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_inicio")]
        ]
        await query.edit_message_text(
            text="💳 **Top Up Balance**\nClick below to simulate adding funds or ask admin.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("pay_"):
        cantidad = data.split("_")[1]
        saldos_usuarios[user_id] = saldos_usuarios.get(user_id, 0.0) + float(cantidad)
        keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_inicio")]]
        await query.edit_message_text(
            text=f"✅ ¡Simulación de recarga exitosa! Se han acreditado `₹{cantidad}` a tu cuenta.\n💰 Nuevo Saldo: `₹{saldos_usuarios[user_id]:.2f}`",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data == "menu_orders":
        orders = historial_keys.get(user_id, [])
        texto_orders = "🔑 **Your Orders / Keys:**\n\n"
        if not orders:
            texto_orders += "No keys purchased yet."
        else:
            for idx, item in enumerate(orders, 1):
                texto_orders += f"{idx}. **{item['producto']} ({item['plan']})**\n   `{item['key']}`\n\n"
        
        keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_inicio")]]
        await query.edit_message_text(text=texto_orders, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ==================== COMANDOS ADMIN ====================
async def agregar_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ No permissions.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: `/agregar [user_id] [amount]`", parse_mode="Markdown")
        return

    try:
        target_user_id = int(context.args[0])
        cantidad = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ ID and amount must be numbers.")
        return

    actual = saldos_usuarios.get(target_user_id, 0.0)
    nuevo_saldo = actual + cantidad
    saldos_usuarios[target_user_id] = nuevo_saldo

    await update.message.reply_text(f"✅ Balance updated for `N{target_user_id}`. New total: **₹{nuevo_saldo:.2f}**", parse_mode="Markdown")

# ==================== MAIN ====================
def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("comprar", cmd_comprar))
    application.add_handler(CommandHandler("agregar", agregar_saldo))
    application.add_handler(CallbackQueryHandler(boton_callback))

    print("Bot iniciado correctamente con comando /comprar habilitado.")
    application.run_polling()

if __name__ == "__main__":
    main()
