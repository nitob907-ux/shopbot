import os
import random
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8762699505:AAEZfO5dOWb_1Ne7H1bFWStuksMGk7iD4x8"
ADMIN_USERNAME = "nirobexe"
ADMIN_CHAT_ID = 7809529766
PAYMENT_NUMBER = "01831297268"
SHOP_NAME = "NIROB FILE SHOP"

PRODUCTS = {
    "multispace": {"name": "Multispace APK", "price": 100, "link": "https://drive.google.com/file/d/1uhCjfnukGloEGowwcE8Mg-b4qf0OeQY8/view?usp=drivesdk"},
    "shelter": {"name": "Shelter APK", "price": 100, "link": "https://drive.google.com/file/d/1I_cmP66GgmUEjJdED2s1bEij_P4Z5hzN/view?usp=drivesdk"},
    "moviebox": {"name": "Movie Box APK", "price": 120, "link": "https://drive.google.com/file/d/1vHj54HSfvIhyIuDzWHmLjT9LdN_LCBlM/view?usp=drivesdk"},
}

TUTORIALS = {
    "multispace": "Multispace APK install korar niom:\n1. APK download korun\n2. Unknown sources enable korun\n3. APK install korun\n4. Open kore enjoy korun!",
    "shelter": "Shelter APK install korar niom:\n1. APK download korun\n2. Unknown sources enable korun\n3. APK install korun\n4. Open kore enjoy korun!",
    "moviebox": "Movie Box APK install korar niom:\n1. APK download korun\n2. Unknown sources enable korun\n3. APK install korun\n4. Movies enjoy korun!",
}

# Database (in-memory)
users = {}  # {user_id: {name, balance, orders, referral_code, referred_by, spin_used}}
pending_orders = {}  # {user_id: product_key}
order_history = {}  # {user_id: [{product, price, date}]}

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


def get_user(user_id, name="User"):
    if user_id not in users:
        ref_code = f"REF{user_id}"[-8:]
        users[user_id] = {"name": name, "balance": 0, "orders": 0, "referral_code": ref_code, "referred_by": None, "spin_used": False}
    return users[user_id]


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ Shop Now", callback_data="products")],
        [InlineKeyboardButton("📦 My Orders", callback_data="my_orders"), InlineKeyboardButton("👤 Profile", callback_data="profile")],
        [InlineKeyboardButton("💰 Add Balance", callback_data="add_balance"), InlineKeyboardButton("🎁 Referral", callback_data="referral")],
        [InlineKeyboardButton("🎰 Lucky Spin", callback_data="lucky_spin")],
        [InlineKeyboardButton("📖 Tutorials", callback_data="tutorials"), InlineKeyboardButton("📞 Support", callback_data="support")],
    ])


def welcome_text(name):
    return (
        f"🏪 ═══ {SHOP_NAME} ═══ 🏪\n\n"
        f"👋 Welcome, {name}!\n\n"
        f"⭐ ═══ SHOP FEATURES ═══ ⭐\n"
        f"├ 📱 Premium APK Files\n"
        f"├ ⚡ Fast Delivery\n"
        f"├ 🔒 Secure Payment\n"
        f"├ 💎 Best Prices\n"
        f"├ 🎁 Referral Rewards\n"
        f"└ 🏆 24/7 Support\n\n"
        f"🚀 Niche theke shuru korun!"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id

    # Check referral
    if context.args and context.args[0].startswith("REF"):
        ref_code = context.args[0]
        for ref_uid, ref_data in users.items():
            if ref_data["referral_code"] == ref_code and ref_uid != uid:
                u = get_user(uid, user.first_name)
                if not u["referred_by"]:
                    u["referred_by"] = ref_uid
                    users[ref_uid]["balance"] += 20
                    await context.bot.send_message(chat_id=ref_uid, text=f"🎉 Apnar referral link use kore {user.first_name} join koreche!\n💰 +20 TK balance added!")
                break

    if user.username and user.username.lower() == ADMIN_USERNAME.lower():
        ADMIN_CHAT_ID_local = uid
        await update.message.reply_text(
            f"👑 Admin Panel\n\n"
            f"📋 /orders - Pending orders\n"
            f"/approve USER_ID - Approve order\n"
            f"/broadcast MSG - Sob user ke message\n"
            f"/addbalance USER_ID AMOUNT - Balance add"
        )
        return

    get_user(uid, user.first_name)
    await update.message.reply_text(welcome_text(user.first_name), reply_markup=main_menu_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id
    user_data = get_user(uid, query.from_user.first_name)

    if data == "main_menu":
        await query.edit_message_text(welcome_text(query.from_user.first_name), reply_markup=main_menu_keyboard())

    elif data == "products":
        keyboard = [
            [InlineKeyboardButton(f"📦 {p['name']} - {p['price']} TK", callback_data=f"buy_{key}")]
            for key, p in PRODUCTS.items()
        ]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        await query.edit_message_text("🛍️ Amader Products:\n\nKinte chaile select korun 👇", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("buy_"):
        key = data[4:]
        product = PRODUCTS.get(key)
        if product:
            balance = user_data["balance"]
            pending_orders[uid] = key
            pay_needed = max(0, product["price"] - balance)
            msg = (
                f"✅ {product['name']} Order\n\n"
                f"💰 Mullo: {product['price']} TK\n"
                f"💳 Apnar Balance: {balance} TK\n"
                f"💵 Pay korte hobe: {pay_needed} TK\n\n"
            )
            if pay_needed > 0:
                msg += f"📲 Bkash/Nagad: {PAYMENT_NUMBER}\n\nPayment er por screenshot pathao! 👇"
            else:
                msg += "✅ Balance diye pay kora hobe! Confirm korun."
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="products")]]
            if pay_needed == 0:
                keyboard.insert(0, [InlineKeyboardButton("✅ Confirm Order", callback_data=f"confirm_{key}")])
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("confirm_"):
        key = data[8:]
        product = PRODUCTS.get(key)
        if product and user_data["balance"] >= product["price"]:
            user_data["balance"] -= product["price"]
            user_data["orders"] += 1
            if uid not in order_history:
                order_history[uid] = []
            order_history[uid].append({"product": product["name"], "price": product["price"]})
            pending_orders.pop(uid, None)
            await query.edit_message_text(
                f"✅ Order Confirmed!\n\n📦 {product['name']}\n\n⬇️ Download Link:\n{product['link']}\n\nDhonnobad! 🙏",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Home", callback_data="main_menu")]])
            )

    elif data == "my_orders":
        history = order_history.get(uid, [])
        if not history:
            msg = "📦 Apnar kono order nei abono."
        else:
            msg = f"📦 Apnar Orders ({len(history)} ta):\n\n"
            for i, o in enumerate(history[-5:], 1):
                msg += f"{i}. {o['product']} - {o['price']} TK\n"
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]))

    elif data == "profile":
        msg = (
            f"👤 Apnar Profile\n\n"
            f"📛 Name: {query.from_user.first_name}\n"
            f"🆔 ID: {uid}\n"
            f"💰 Balance: {user_data['balance']} TK\n"
            f"📦 Total Orders: {user_data['orders']}\n"
            f"🎁 Referral Code: {user_data['referral_code']}\n"
        )
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]))

    elif data == "add_balance":
        await query.edit_message_text(
            f"💰 Balance Add Korun\n\n"
            f"📲 Bkash/Nagad: {PAYMENT_NUMBER}\n\n"
            f"Minimum: 50 TK\n\n"
            f"Payment er por screenshot pathao - amount likhe dao!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]))

    elif data == "referral":
        bot_username = "NirobFileShopBot"
        ref_link = f"https://t.me/{bot_username}?start={user_data['referral_code']}"
        msg = (
            f"🎁 Referral System\n\n"
            f"🔗 Apnar Link:\n{ref_link}\n\n"
            f"💰 Reward: Protiti referral e 20 TK!\n\n"
            f"Link share korun o balance earn korun! 🚀"
        )
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]))

    elif data == "lucky_spin":
        if user_data["spin_used"]:
            await query.edit_message_text(
                "🎰 Lucky Spin\n\n❌ Apni ajke already spin korechen!\nKal abar ashun. 😊",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]))
        else:
            prizes = [0, 0, 5, 10, 20, 50, 0, 0, 5, 10]
            prize = random.choice(prizes)
            user_data["spin_used"] = True
            user_data["balance"] += prize
            if prize > 0:
                msg = f"🎰 Lucky Spin Result!\n\n🎉 Congratulations!\n💰 Apni {prize} TK jitechen!\n\n💳 Balance update hoyeche!"
            else:
                msg = "🎰 Lucky Spin Result!\n\n😔 Ei baar hoyni!\nKal abar try korun. 🍀"
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]))

    elif data == "tutorials":
        keyboard = [
            [InlineKeyboardButton(f"📖 {p['name']}", callback_data=f"tut_{key}")]
            for key, p in PRODUCTS.items()
        ]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        await query.edit_message_text("📖 Tutorials:\n\nKon APK er tutorial dekhte chan?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("tut_"):
        key = data[4:]
        tut = TUTORIALS.get(key, "Tutorial paoa jaini.")
        await query.edit_message_text(f"📖 {PRODUCTS[key]['name']} Tutorial:\n\n{tut}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="tutorials")]]))

    elif data == "support":
        await query.edit_message_text(
            f"📞 Support\n\nAdmin: @{ADMIN_USERNAME}\nBkash/Nagad: {PAYMENT_NUMBER}\n\n24/7 support available! 🏆",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    user_data = get_user(uid, user.first_name)

    if update.message.photo and uid in pending_orders:
        pkey = pending_orders.get(uid)
        product = PRODUCTS.get(pkey, {})
        caption = update.message.caption or ""
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=update.message.photo[-1].file_id,
            caption=(
                f"💰 Notun Payment!\n\n"
                f"👤 User: {user.full_name}\n"
                f"🆔 ID: {uid}\n"
                f"📦 Product: {product.get('name', pkey)}\n"
                f"💵 Price: {product.get('price', '?')} TK\n"
                f"📝 Note: {caption}\n\n"
                f"Approve: /approve {uid}"
            )
        )
        await update.message.reply_text("✅ Screenshot pathano hoyeche!\nAdmin verify korle apnake link pathabe. Ektu opekha korun. 🙏")
        return

    await update.message.reply_text("/start likun othoba button use korun.")


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
        msg += f"👤 User ID: {uid}\n📦 {p.get('name', pkey)}\n💵 {p.get('price', '?')} TK\nApprove: /approve {uid}\n\n"
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
        await update.message.reply_text("Invalid ID.")
        return
    if uid not in pending_orders:
        await update.message.reply_text(f"User {uid} er kono pending order nei.")
        return
    pkey = pending_orders.pop(uid)
    product = PRODUCTS.get(pkey)
    if product:
        user_data = get_user(uid)
        user_data["orders"] += 1
        if uid not in order_history:
            order_history[uid] = []
        order_history[uid].append({"product": product["name"], "price": product["price"]})
        await context.bot.send_message(
            chat_id=uid,
            text=f"✅ Payment Confirmed!\n\n📦 {product['name']}\n\n⬇️ Download Link:\n{product['link']}\n\nDhonnobad amader shop e order korar jonno! 🙏"
        )
        await update.message.reply_text(f"✅ User {uid} ke link pathano hoyeche!")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user.username or user.username.lower() != ADMIN_USERNAME.lower():
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast MESSAGE")
        return
    msg = " ".join(context.args)
    count = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 Admin Message:\n\n{msg}")
            count += 1
        except:
            pass
    await update.message.reply_text(f"✅ {count} joner kache message pathano hoyeche!")


async def addbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user.username or user.username.lower() != ADMIN_USERNAME.lower():
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addbalance USER_ID AMOUNT")
        return
    try:
        uid = int(context.args[0])
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Invalid input.")
        return
    user_data = get_user(uid)
    user_data["balance"] += amount
    await context.bot.send_message(chat_id=uid, text=f"💰 Apnar account e {amount} TK add hoyeche!\nTotal Balance: {user_data['balance']} TK")
    await update.message.reply_text(f"✅ User {uid} er balance {amount} TK added!")


def main():
    thread = threading.Thread(target=run_web_server, daemon=True)
    thread.start()
    logger.info("Web server started")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CommandHandler("approve", approve_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("addbalance", addbalance_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    logger.info("Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()
