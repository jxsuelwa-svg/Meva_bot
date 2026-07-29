import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# ==================== CONFIGURACIÓN ====================
TELEGRAM_BOT_TOKEN = "8423978432:AAGPiQbhmD3C1i9F7Q97mr-37SeqG0x1038"
PAYPAL_ME_LINK = "https://paypal.me/TuUsuarioPayPal"

# Tu ID de administrador
ADMIN_IDS = [7390841762]

# Catálogo basado en las capturas anteriores
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
            }
        }
    },
    "pc": {
        "nombre": "💻 PANEL STORE — 💻 PC",
        "productos": {
            "aimsilent": {
                "nombre": "AIMSILENT EXE (STREAMER)",
                "planes": {
                    "1d": {"tiempo": "1 Day", "precio": 120},
                    "7d": {"tiempo": "7 Days", "precio": 500}
                }
            },
            "basic_pc": {
                "nombre": "BASIC (STREAMPROOF + SAFE )",
                "planes": {
                    "1d": {"tiempo": "1 Day", "precio": 100},
                    "30d": {"tiempo": "30 Days", "precio": 950}
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
        f"🎉 **Yo {user_name}, Welcome Back!!**\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"▫️ **PIN de cliente: N{user_id}**\n"
        f"💰 **Meu saldo é: ₹{saldo:.2f}**\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"❓ **Why our store is trusted?**\n"
        f"└ Direct deals with every mod developer\n"
        f"└ Instant delivery after payment\n"
        f"└ **5% discount** on your 2nd & every extra purchase\n"
        f"└ Guaranteed discounted prices"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛒 Shop Now", callback_data="menu_shop")],
        [
            InlineKeyboardButton("🔑 My Orders", callback_data="menu_orders"),
            InlineKeyboardButton("👤 Profile", callback_data="menu_profile")
        ],
        [
            InlineKeyboardButton("💳 Pay Proof", callback_data="menu_recargar"),
            InlineKeyboardButton("❓ How to Use", callback_data="menu_help")
        ],
        [
            InlineKeyboardButton("🛠 Support", callback_data="menu_support"),
            InlineKeyboardButton("🎡 Spin & Win", callback_data="menu_spin")
        ],
        [InlineKeyboardButton("🎁 Referral — Invite & Earn Spins", callback_data="menu_referral")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update_or_query, "message") and update_or_query.message:
        await update_or_query.message.reply_text(texto, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update_or_query.edit_message_text(text=texto, reply_markup=reply_markup, parse_mode="Markdown")

# ==================== COMANDO START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await mostrar_menu_principal(update, context, user.id, user.first_name)

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
            [InlineKeyboardButton("💻 PC", callback_data="cat_pc")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_inicio")]
        ]
        await query.edit_message_text(
            text="🛒 **PANEL STORE — SHOP**\n\n🔥 Choose your device category:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("cat_"):
        cat_id = data.split("_")[1]
        if cat_id not in CATALOGO:
            keyboard = [[InlineKeyboardButton("⬅️ Back to Shop", callback_data="menu_shop")]]
            await query.edit_message_text(text="🚧 Category coming soon or not available.", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        cat_data = CATALOGO[cat_id]
        keyboard = []
        for prod_key, prod_info in cat_data["productos"].items():
            keyboard.append([InlineKeyboardButton(prod_info["nombre"], callback_data=f"prod_{cat_id}_{prod_key}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back to Categories", callback_data="menu_shop")])

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
                cb_data = f"buy_{cat_id}_{prod_key}_{plan_key}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=cb_data)])
        
        keyboard.append([InlineKeyboardButton("🎬 Watch Gameplay Video", url="https://youtube.com")])
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

    elif data.startswith("buy_"):
        partes = data.split("_")
        cat_id, prod_key, plan_key = partes[1], partes[2], partes[3]
        await procesar_compra_key(query, user_id, cat_id, prod_key, plan_key)

    elif data == "menu_recargar":
        keyboard = [
            [InlineKeyboardButton("💵 Top up ₹100", callback_data="pay_100"),
             InlineKeyboardButton("💵 Top up ₹500", callback_data="pay_500")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_inicio")]
        ]
        await query.edit_message_text(
            text="💳 **Top Up Balance via PayPal**\nSelect amount:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("pay_"):
        cantidad = data.split("_")[1]
        enlace_pago = f"{PAYPAL_ME_LINK}/{cantidad}USD"
        keyboard = [
            [InlineKeyboardButton("💳 Pay via PayPal", url=enlace_pago)],
            [InlineKeyboardButton("🔄 I Have Paid (Notify Admin)", callback_data=f"notificar_pago_{cantidad}")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_inicio")]
        ]
        await query.edit_message_text(
            text=f"🛒 **Top Up ₹{cantidad}**\n\n1. Click button to pay.\n2. Click 'I Have Paid' to notify admin.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("notificar_pago_"):
        cantidad = data.split("_")[2]
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"🔔 **Payment Alert!**\n👤 User: @{user_name} (`{user_id}`)\n💵 Amount: `₹{cantidad}`\n\nApprove with:\n`/agregar {user_id} {cantidad}`",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
        keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_inicio")]]
        await query.edit_message_text(text="✅ Notification sent to admin successfully!", reply_markup=InlineKeyboardMarkup(keyboard))

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

    elif data in ["menu_help", "menu_support", "menu_spin", "menu_referral"]:
        keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_inicio")]]
        await query.edit_message_text(
            text="ℹ️ **Information / Support**\nContact the administrator for assistance or rewards redemption.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

# ==================== GENERACIÓN AUTOMÁTICA DE KEYS ====================
async def procesar_compra_key(query, user_id, cat_id, prod_key, plan_key):
    prod_info = CATALOGO[cat_id]["productos"][prod_key]
    plan_info = prod_info["planes"][plan_key]
    precio = plan_info["precio"]
    nombre_producto = prod_info["nombre"]
    tiempo_plan = plan_info["tiempo"]

    saldo_actual = saldos_usuarios.get(user_id, 0.0)

    if saldo_actual < precio:
        keyboard = [[InlineKeyboardButton("⬅️ Back to Shop", callback_data=f"prod_{cat_id}_{prod_key}")]]
        await query.edit_message_text(
            text=f"❌ **Insufficient Balance!**\nRequired: `₹{precio}`\nYour Balance: `₹{saldo_actual}`",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    # Descontar saldo y generar Key única
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
             f"💰 Remaining Balance: `₹{saldos_usuarios[user_id]:.2f}`\n\n"
             f"*(Saved in 'My Orders')*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ==================== COMANDOS ADMIN ====================
async def ver_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    saldo = saldos_usuarios.get(user_id, 0.0)
    await update.message.reply_text(f"▫️ PIN de cliente: `N{user_id}`\n💰 Balance: `₹{saldo:.2f}`", parse_mode="Markdown")

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
    
    try:
        await context.bot.send_message(chat_id=target_user_id, text=f"🎉 Top-up of `₹{cantidad:.2f}` approved!\n💰 New Balance: `₹{nuevo_saldo:.2f}`", parse_mode="Markdown")
    except Exception:
        pass

# ==================== MAIN ====================
def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("saldo", ver_saldo))
    application.add_handler(CommandHandler("agregar", agregar_saldo))
    application.add_handler(CallbackQueryHandler(boton_callback))

    print("Iniciando bot estilo Panel Store con PIN de cliente...")
    application.run_polling()

if __name__ == "__main__":
    main()
