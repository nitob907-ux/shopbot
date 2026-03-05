import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8762699505:AAEZfO5dOWb_1Ne7H1bFWStuksMGk7iD4x8"
ADMIN_USERNAME = "nirobexe"
PAYMENT_NUMBER = "01831297268"
ADMIN_CHAT_ID = None  # Will be set when admin uses /start

PRODUCTS = {
    "multispace": {
        "name": "Multispace APK",
        "price": 100,
        "link": "https://drive.google.com/file/d/1uhCjfnukGloEGowwcE8Mg-b4qf0OeQY8/view?usp=drivesdk"
    },
    "shelter": {
        "name": "Shelter APK",
        "price": 100,
        "link": "https://drive.google.com/file/d/1I_cmP66GgmUEjJdED2s1bEij_P4Z5hzN/view?usp=drivesdk"
    },
    "moviebox": {
        "name": "Movie Box APK",
        "price": 120,
        "link": "https://drive.google.com/file/d/1vHj54HSfvIhyIuDzWHmLjT9LdN_LCBlM/view?usp=drivesdk"
    },
}

# pending_orders: {user_id: product_key}
pending_orders = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Nirob Shop Bot is running!")

    def log_message(self, format, *args):
        pass


def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), PingHandler)
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_CHAT_ID
    user = update.effective_user
    if user.username and user.username.lower() == ADMIN_USERNAME.lower():
        ADMIN_CHAT_ID = update.effective_chat.id
        await update.message.reply_text(
            f"👑 Admin panel e swagotom!\n\n"
            f"Pending orders dekhte: /orders\n"
            f"Approve korte: /approve USER_ID\n\n"
            f"Admin chat ID: {ADMIN_CHAT_ID}"
        )
        return

    keyboard = [
        [InlineKeyboardButton("🛍️ Ponno Dekhun", callback_data="products")],
        [InlineKeyboardButton("📞 Support", callback_data="support")],
    ]
    await update.message.reply_text(
        "🤖 Nirob File Shop e swagotom!\nNiche button theke ponno dekhun o order korun.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user.username or user.username.lower() != ADMIN_USERNAME.lower():
        return
    if not pending_orders:
        await update.message.reply_text("📭 Kono pending order nei.")
        return
    msg = "📋 Pending Orders:\n\n"
    for uid, pkey in pending_orders.items():
        p = PRODUCTS.get(pkey, {})
        msg += f"👤 User ID: {uid}\n📦 Product: {p.get('name', pkey)}\n💰 Price: {p.get('price', '?')} TK\nApprove: /approve {uid}\n\n"
    await update.message.reply_text(msg)


async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user.username or user.username.lower() != ADMIN_USERNAME.lower():
        return
    if not context.args:
        await update.message.reply_text("Usage: /approve USER_ID")
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user ID.")
        return
    if uid not in pending_orders:
        await update.message.reply_text(f"User {uid} er kono pending order nei.")
        return
    pkey = pending_orders.pop(uid)
    product = PRODUCTS.get(pkey)
    if product:
        await context.bot.send_message(
            chat_id=uid,
            text=f"✅ Payment confirm hoyeche!\n\n"
                 f"📦 {product['name']} er download link:\n\n"
                 f"👇 {product['link']}\n\n"
                 f"Dhonnobad amader shop e order korar jonno! 🙏"
        )
        await update.message.reply_text(f"✅ User {uid} ke link pathano hoyeche!")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "products":
        keyboard = [
            [InlineKeyboardButton(f"📦 {p['name']} - {p['price']} TK", callback_data=f"buy_{key}")]
            for key, p in PRODUCTS.items()
        ]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
        await query.edit_message_text(
            "🛍️ Amader ponnosamuho:\n\nKinte chaile niche button chapu.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("buy_"):
        key = data[4:]
        product = PRODUCTS.get(key)
        if product:
            user_id = query.from_user.id
            pending_orders[user_id] = key
            await query.edit_message_text(
                f"✅ {product['name']} order:\n\n"
                f"💰 Mullo: {product['price']} TK\n\n"
                f"📲 Bkash/Nagad: {PAYMENT_NUMBER}\n\n"
                f"⚠️ Payment korar por niche screenshot pathao!\n"
                f"Screenshot pathanor por admin verify korbe o link pathabe.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="products")]
                ])
            )

    elif data == "support":
        await query.edit_message_text(
            f"📞 Support:\nAdmin: @{ADMIN_USERNAME}\nBkash/Nagad: {PAYMENT_NUMBER}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("🛍️ Ponno Dekhun", callback_data="products")],
            [InlineKeyboardButton("📞 Support", callback_data="support")],
        ]
        await query.edit_message_text(
            "🤖 Nirob File Shop e swagotom!\nNiche button theke ponno dekhun o order korun.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id

    # If user has pending order and sends photo (screenshot)
    if update.message.photo and uid in pending_orders:
        pkey = pending_orders.get(uid)
        product = PRODUCTS.get(pkey, {})
        # Notify admin
        if ADMIN_CHAT_ID:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=update.message.photo[-1].file_id,
                caption=f"💰 Notun payment screenshot!\n\n"
                        f"👤 User: {user.full_name}\n"
                        f"🆔 User ID: {uid}\n"
                        f"📦 Product: {product.get('name', pkey)}\n"
                        f"💵 Price: {product.get('price', '?')} TK\n\n"
                        f"Approve korte: /approve {uid}"
            )
        await update.message.reply_text(
            "✅ Screenshot pathano hoyeche!\nAdmin verify korle apnake link pathabe. Ektu opekha korun. 🙏"
        )
        return

    await update.message.reply_text("/start likun othoba button use korun.")


def main():
    thread = threading.Thread(target=run_web_server, daemon=True)
    thread.start()
    logger.info("Web server started")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CommandHandler("approve", approve_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    logger.info("Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()
