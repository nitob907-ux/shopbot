#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

BOT_TOKEN = "8762699505:AAEZfO5dOWb_1Ne7H1bFWStuksMGk7iD4x8"
ADMIN_USERNAME = "@nirobfileshopbot"

PRODUCTS = {
    "mod_1": {
        "name": "🛒 MULTISPACE APK",
        "price": "৳ ১০০",
        "description": "Multispace APK — একই ফোনে দুইটা অ্যাকাউন্ট চালাও!",
        "emoji": "📱"
    },
    "mod_2": {
        "name": "🛒 SHELTER APK",
        "price": "৳ ১০০",
        "description": "Shelter APK — অ্যাপ আলাদা রাখো, প্রাইভেসি নিরাপদ!",
        "emoji": "🏠"
    },
    "mod_3": {
        "name": "🛒 MOVIE BOX APK",
        "price": "৳ ১২০",
        "description": "Movie Box APK — ফ্রিতে মুভি ও সিরিজ দেখো!",
        "emoji": "🎬"
    },
}

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛒 প্রোডাক্ট দেখো", callback_data="show_products")],
        [InlineKeyboardButton("📞 সাপোর্ট / অর্ডার করো", callback_data="support")],
        [InlineKeyboardButton("ℹ️ আমাদের সম্পর্কে", callback_data="about")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"🎮 *স্বাগতম {user.first_name}!*\n\n"
        f"Nirob File Shop এ তোমাকে স্বাগত জানাই! 🔥\n\n"
        f"সেরা APK ফাইল পাওয়ার একমাত্র ঠিকানা।\n\n"
        f"নিচের বাটন থেকে বেছে নাও 👇"
    )
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for prod_id, prod in PRODUCTS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{prod['emoji']} {prod['name']} — {prod['price']}",
                callback_data=f"product_{prod_id}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🏠 হোমে ফিরে যাও", callback_data="home")])
    await query.edit_message_text(
        "🛒 *প্রোডাক্ট সিলেক্ট করো:*\n\nযেকোনো প্রোডাক্টে ক্লিক করো 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prod_id = query.data.replace("product_", "")
    prod = PRODUCTS.get(prod_id)
    if not prod:
        await query.edit_message_text("❌ প্রোডাক্ট পাওয়া যায়নি।")
        return
    text = (
        f"{prod['emoji']} *{prod['name']}*\n\n"
        f"📝 বিবরণ: {prod['description']}\n\n"
        f"💰 মূল্য: *{prod['price']}*\n\n"
        f"অর্ডার করতে নিচের বাটনে ক্লিক করো 👇"
    )
    keyboard = [
        [InlineKeyboardButton("✅ অর্ডার করো", callback_data=f"order_{prod_id}")],
        [InlineKeyboardButton("🔙 পিছনে যাও", callback_data="show_products")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def place_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prod_id = query.data.replace("order_", "")
    prod = PRODUCTS.get(prod_id)
    user = query.from_user
    order_text = (
        f"✅ *অর্ডার নেওয়া হয়েছে!*\n\n"
        f"🛒 প্রোডাক্ট: {prod['name']}\n"
        f"💰 মূল্য: {prod['price']}\n\n"
        f"📲 পেমেন্ট ও ডেলিভারির জন্য যোগাযোগ করো:\n"
        f"👉 {ADMIN_USERNAME}\n\n"
        f"অর্ডার নম্বর: *#ORD{user.id}{prod_id[-1]}*\n\n"
        f"ধন্যবাদ! 🙏"
    )
    keyboard = [
        [InlineKeyboardButton("📞 এখনই যোগাযোগ করো", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("🏠 হোমে ফিরে যাও", callback_data="home")],
    ]
    await query.edit_message_text(order_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        f"📞 *সাপোর্ট ও যোগাযোগ*\n\n"
        f"যেকোনো সমস্যা বা অর্ডারের জন্য:\n\n"
        f"👤 অ্যাডমিন: {ADMIN_USERNAME}\n"
        f"⏰ সময়: সকাল ৯টা — রাত ১১টা\n\n"
        f"আমরা সবসময় সাহায্য করতে প্রস্তুত! 😊"
    )
    keyboard = [
        [InlineKeyboardButton("💬 অ্যাডমিনকে মেসেজ করো", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("🏠 হোমে ফিরে যাও", callback_data="home")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "ℹ️ *আমাদের সম্পর্কে*\n\n"
        "📱 Nirob File Shop — বিশ্বস্ত APK শপ\n\n"
        "✅ ১০০% অরিজিনাল ফাইল\n"
        "✅ দ্রুত ডেলিভারি\n"
        "✅ সাশ্রয়ী মূল্য\n"
        "✅ ২৪/৭ কাস্টমার সাপোর্ট\n\n"
        "আমাদের বিশ্বাস করো! 🔥"
    )
    keyboard = [[InlineKeyboardButton("🏠 হোমে ফিরে যাও", callback_data="home")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    welcome_text = (
        f"🎮 *স্বাগতম {user.first_name}!*\n\n"
        f"Nirob File Shop এ তোমাকে স্বাগত! 🔥\n\n"
        f"নিচের বাটন থেকে বেছে নাও 👇"
    )
    await query.edit_message_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 /start টাইপ করো অথবা মেনু থেকে বেছে নাও।",
        reply_markup=main_menu_keyboard()
    )

def main():
    print("🤖 বট চালু হচ্ছে...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_products, pattern="^show_products$"))
    app.add_handler(CallbackQueryHandler(product_detail, pattern="^product_"))
    app.add_handler(CallbackQueryHandler(place_order, pattern="^order_"))
    app.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(home, pattern="^home$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ বট রেডি!")
    app.run_polling()

if __name__ == "__main__":
    main()
