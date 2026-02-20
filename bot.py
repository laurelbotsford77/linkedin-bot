import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7195911336  # এখানে তোমার Telegram ID বসাও

# Database
conn = sqlite3.connect("accounts.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    user_id INTEGER,
    age INTEGER,
    connections INTEGER,
    price TEXT,
    submit_date TEXT,
    payment_status TEXT,
    payment_date TEXT
)
""")
conn.commit()

def calculate_price(age, connections):
    if age == 1 and connections == 0:
        return "500 Taka"
    elif age == 2 and connections >= 100:
        return "1000 Taka"
    elif age == 3 and connections >= 300:
        return "1500 Taka"
    else:
        return "Manual Review"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Check Price", callback_data='price')],
        [InlineKeyboardButton("📞 Contact Admin", callback_data='contact')],
    ]
    await update.message.reply_text(
        "Welcome to LinkedIn Buyer Bot",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "price":
        await query.message.reply_text("Send Age and Connections\nExample: 2 150")

    elif query.data == "contact":
        await query.message.reply_text(
            "Contact Admin:\n"
            "WhatsApp: 01944190032\n"
            "Telegram: @KAMRULxORJINAL"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age, connections = map(int, update.message.text.split())
        price = calculate_price(age, connections)
        submit_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute("""
            INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (update.message.from_user.id, age, connections,
              price, submit_date, "Pending", "None"))
        conn.commit()

        await update.message.reply_text(f"Estimated Price: {price}")

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"""
New Submission
User: {update.message.from_user.id}
Age: {age}
Connections: {connections}
Price: {price}
Submitted: {submit_date}
Status: Pending
"""
        )

    except:
        await update.message.reply_text("Format Error. Example: 2 150")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

app.run_polling()
