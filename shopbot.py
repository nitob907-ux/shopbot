import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

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

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Nirob Shop Bot is running!")
    def log_message(self, format, *args):
        pass

def run_web_server():
    server = HTTPServer(("0.0.0.0", 8080), PingHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ponno Dekhun", callback_data="products")],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    await update.message.reply_text(
        "Nirob File Shop e swagotom!\nNiche button theke ponno dekhun.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "products":
        keyboard = [
            [InlineKeyboardButton(f"{p['name']} - {p['price']} TK", callback_data=f"buy_{key}")]
            for key, p in PRODUCTS.items()
        ]
        keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
        await query.edit_message_text(
            "Amader ponnosamuho:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("buy_"):
        key = data[4:]
        product = PRODUCTS.get(key)
        if product:
            await query.edit_message_text(
                f"{product['name']} order korte:\n\n"
                f"Mullo: {product['price']} TK\n\n"
                f"Bkash/Nagad: {PAYMENT_NUMBER}\n\n"
                f"Payment er por screenshot pathan.\n"
                f"Admin: @{ADMIN_USERNAME}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Back", callback_data="products")]
                ])
            )

    elif data == "support":
        await query.edit_message_text(
            f"Support:\nAdmin: @{ADMIN_USERNAME}\nBkash/Nagad: {PAYMENT_NUMBER}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back", callback_data="back")]
            ])
        )

    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("Ponno Dekhun", callback_data="products")],
            [InlineKeyboardButton("Support", callback_data="support")],
        ]
        await query.edit_message_text(
            "Nirob File Shop e swagotom!\nNiche button theke ponno dekhun.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start likun othoba button use korun.")

def main():
    thread = threading.Thread(target=run_web_server, daemon=True)
    thread.start()
    logger.info("Web server started on port 8080")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
