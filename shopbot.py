import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BOT_TOKEN = "8762699505:AAEZfO5dOWb_1Ne7H1bFWStuksMGk7iD4x8"
ADMIN_USERNAME = "nirobfileshopbot"
PAYMENT_NUMBER = "01831297268"

PRODUCTS = {
    "multispace": {"name": "Multispace APK", "price": 100},
    "shelter":    {"name": "Shelter APK",    "price": 100},
    "moviebox":   {"name": "Movie Box APK",  "price": 120},
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── WEB SERVER (keeps Render alive) ──────────────────────────────────────────
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Nirob Shop Bot is running!")

    def log_message(self, format, *args):
        pass  # silence access logs

def run_web_server():
    server = HTTPServer(("0.0.0.0", 8080), PingHandler)
    server.serve_forever()

# ─── BOT HANDLERS ─────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛍️ পণ্য দেখুন", callback_data="products")],
        [InlineKeyboardButton("📞 সাপোর্ট", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤖 *Nirob File Shop* এ স্বাগতম!\n\n"
        "নিচের বাটন থেকে পণ্য দেখুন এবং অর্ডার করুন।",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "products":
        keyboard = [
            [InlineKeyboardButton(f"📦 {p['name']} — {p['price']} TK", callback_data=f"buy_{key}")]
            for key, p in PRODUCTS.items()
        ]
        keyboard.append([InlineKeyboardButton("🔙 ফিরে যান", callback_data="back")])
        await query.edit_message_text(
            "🛍️ *আমাদের পণ্যসমূহ:*\n\nকিনতে চাইলে নিচের বাটনে চাপুন।",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("buy_"):
        key = data[4:]
        product = PRODUCTS.get(key)
        if product:
            await query.edit_message_text(
                f"✅ *{product['name']}* অর্ডার করতে:\n\n"
                f"💰 মূল্য: *{product['price']} TK*\n\n"
                f"📲 বিকাশ/নগদ: `{PAYMENT_NUMBER}`\n\n"
                f"পেমেন্ট করার পর স্ক্রিনশট পাঠান।\n"
                f"Admin: @{ADMIN_USERNAME}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 পণ্যে ফিরুন", callback_data="products")]
                ])
            )

    elif data == "support":
        await query.edit_message_text(
            f"📞 *সাপোর্ট:*\n\nAdmin: @{ADMIN_USERNAME}\n"
            f"বিকাশ/নগদ: `{PAYMENT_NUMBER}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 ফিরে যান", callback_data="back")]
            ])
        )

    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("🛍️ পণ্য দেখুন", callback_data="products")],
            [InlineKeyboardButton("📞 সাপোর্ট", callback_data="support")],
        ]
        await query.edit_message_text(
            "🤖 *Nirob File Shop* এ স্বাগতম!\n\nনিচের বাটন থেকে পণ্য দেখুন।",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 /start লিখুন অথবা বাটন ব্যবহার করুন।"
    )

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    # Start web server in background thread
    thread = threading.Thread(target=run_web_server, daemon=True)
    thread.start()
    logger.info("Web server started on port 8080")

    # Start bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
