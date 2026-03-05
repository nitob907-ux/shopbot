from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8762699505:AAEZfO5dOWb_1Ne7H1bFWStuksMGk7iD4x8"
ADMIN_USERNAME = "@nirobfileshopbot"
BKASH_NUMBER = "01831297268"
NAGAD_NUMBER = "01831297268"
PRODUCTS = {
    "mod_1": {"name": "MULTISPACE APK", "price": "100 TK", "description": "একই ফোনে দুইটা একাউন্ট চালাও!", "emoji": "📱"},
    "mod_2": {"name": "SHELTER APK", "price": "100 TK", "description": "প্রাইভেসি নিরাপদ রাখো!", "emoji": "🏠"},
    "mod_3": {"name": "MOVIE BOX APK", "price": "120 TK", "description": "ফ্রিতে মুভি দেখো!", "emoji": "🎬"},
}

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(("0.0.0.0", 8080), HealthHandler)
    server.serve_forever()
    def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛒 প্রোডাক্ট দেখো", callback_data="show_products")],
        [InlineKeyboardButton("📞 সাপোর্ট", callback_data="support")],
        [InlineKeyboardButton("ℹ️ আমাদের সম্পর্কে", callback_data="about")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        "স্বাগতম " + user.first_name + "!\n\nNirob File Shop এ আপনাকে স্বাগত! 🔥\n\nনিচের বাটন থেকে বেছে নিন 👇",
        reply_markup=main_menu_keyboard()
    )
    async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for pid, prod in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(prod["emoji"] + " " + prod["name"] + " — " + prod["price"], callback_data="product_" + pid)])
    keyboard.append([InlineKeyboardButton("🏠 হোম", callback_data="home")])
    await query.edit_message_text("প্রোডাক্ট সিলেক্ট করো 👇", reply_markup=InlineKeyboardMarkup(keyboard))

async def product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pid = query.data.replace("product_", "")
    prod = PRODUCTS.get(pid)
    text = prod["emoji"] + " " + prod["name"] + "\n\n" + prod["description"] + "\n\nমূল্য: " + prod["price"]
    keyboard = [
        [InlineKeyboardButton("✅ অর্ডার করো", callback_data="order_" + pid)],
        [InlineKeyboardButton("🔙 পিছনে", callback_data="show_products")]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    async def place_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pid = query.data.replace("order_", "")
    prod = PRODUCTS.get(pid)
    text = (
        "✅ অর্ডার কনফার্ম!\n\n"
        + prod["name"] + "\n"
        + "মূল্য: " + prod["price"] + "\n\n"
        + "💳 পেমেন্ট করো:\n"
        + "বিকাশ: " + BKASH_NUMBER + "\n"
        + "নগদ: " + NAGAD_NUMBER + "\n\n"
        + "পেমেন্ট করার পর স্ক্রিনশট পাঠাও:\n"
        + ADMIN_USERNAME + "\n\n"
        + "APK পাঠিয়ে দেওয়া হবে! 😊"
    )
    keyboard = [
        [InlineKeyboardButton("📞 অ্যাডমিনকে মেসেজ করো", url="https://t.me/nirobfileshopbot")],
        [InlineKeyboardButton("🏠 হোম", callback_data="home")]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("💬 অ্যাডমিন", url="https://t.me/nirobfileshopbot")],
        [InlineKeyboardButton("🏠 হোম", callback_data="home")]
    ]
    await query.edit_message_text("📞 সাপোর্ট\n\nঅ্যাডমিন: " + ADMIN_USERNAME + "\nসময়: সকাল ৯টা - রাত ১১টা", reply_markup=InlineKeyboardMarkup(keyboard))

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🏠 হোম", callback_data="home")]]
    await query.edit_message_text("ℹ️ Nirob File Shop\n\n✅ অরিজিনাল ফাইল\n✅ দ্রুত ডেলিভারি\n✅ সাশ্রয়ী মূল্য", reply_markup=InlineKeyboardMarkup(keyboard))

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("স্বাগতম! 🔥\n\nনিচের বাটন থেকে বেছে নাও 👇", reply_markup=main_menu_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start দাও অথবা মেনু থেকে বেছে নাও।", reply_markup=main_menu_keyboard())
    def main():
    print("বট চালু হচ্ছে...")
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_products, pattern="^show_products$"))
    app.add_handler(CallbackQueryHandler(product_detail, pattern="^product_"))
    app.add_handler(CallbackQueryHandler(place_order, pattern="^order_"))
    app.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(home, pattern="^home$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("বট রেডি!")
    app.run_polling()

if __name__ == "__main__":
    main()
