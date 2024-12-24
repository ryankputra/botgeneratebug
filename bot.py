import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import base64
import json
import pyotp
import logging
from datetime import datetime

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Konfigurasi Bot
API_TOKEN = '7721294308:AAHTMdqL9WVGwJqSLcgB0NQt-sHJYey3XUM'
ADMIN_ID = 7251232303
bot = telebot.TeleBot(API_TOKEN)

# Penyimpanan data
user_links = {}
user_secrets = {}
active_users = set()
user_data = {}  # Untuk menyimpan informasi pengguna

# Dictionary pilihan bug
bugs = {
    "xl_vidio": "quiz.int.vidio.com",
    "xl_edukasi": "172.67.73.39",
    "telkomsel_ilped": "104.26.7.171",
    "telkomsel_ilped_alt": "104.26.6.171",
    "xl_viu": "zaintest.vuclip.com",
    "xl_vip": "104.17.3.81",
    "byu_opok": "space.byu.id"
}

def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🔄 Generate VMess/Trojan", callback_data="menu_vmess")
    )
    markup.row(
        InlineKeyboardButton("🔑 Generate OTP", callback_data="menu_otp")
    )
    markup.row(
        InlineKeyboardButton("ℹ️ Bantuan", callback_data="menu_help")
    )
    return markup

def welcome_message():
    return '''
🌀Selamat Datang di RyyStore Multi Tools!🌀

Silakan pilih layanan yang Anda butuhkan:

1. 🛜Generate VMess/Trojan
   Bug Yang Tersedia:
   - XL Vidio
   - XL Edukasi
   - XL VIU
   - XL VIP
   - TELKOMSEL ILMUPEDIA

2. 🔑 Generate OTP 2FA
   - Generate kode OTP dari secret 2FA
   - Simpan secret key dengan aman

3. ℹ️ Bantuan
   - Panduan penggunaan
   - Informasi tambahan

Pilih menu di bawah untuk memulai!
'''

@bot.message_handler(commands=['status'])
def handle_status(message):
    # Tautan server
    server_link = "https://stats.uptimerobot.com/3rNrce2g6i"
    
    bot.reply_to(
        message,
        f"🌐 Status server dapat dilihat di tautan berikut:\n\n[Klik di sini untuk melihat status server]({server_link})",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['generate'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"
    first_name = message.from_user.first_name or "No Name"
    
    user_data[user_id] = {
        'username': username,
        'first_name': first_name,
        'join_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    active_users.add(user_id)
    
    bot.send_message(
        message.chat.id,
        welcome_message(),
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['users'])
def show_users(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    users_text = "📊 *Daftar Pengguna Bot*\n\n"
    for user_id, data in user_data.items():
        users_text += f"👤 *Nama:* {data['first_name']}\n"
        users_text += f"🆔 *User ID:* `{user_id}`\n"
        users_text += f"📝 *Username:* @{data['username']}\n"
        users_text += f"📅 *Bergabung:* {data['join_date']}\n"
        users_text += "➖➖➖➖➖➖➖➖➖➖\n"
    
    total_users = len(user_data)
    users_text += f"\n📈 *Total Pengguna:* {total_users}"
    
    max_length = 4096
    if len(users_text) > max_length:
        for x in range(0, len(users_text), max_length):
            bot.send_message(
                message.chat.id,
                users_text[x:x+max_length],
                parse_mode="Markdown"
            )
    else:
        bot.send_message(
            message.chat.id,
            users_text,
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda message: message.text.startswith(("vmess://", "trojan://")))
def handle_link(message):
    user_links[message.from_user.id] = message.text
    bot.reply_to(
        message,
        "Link diterima! Silakan pilih jenis bug:",
        reply_markup=create_bug_keyboard()
    )

# Start bot
print("Bot started...")
bot.polling(none_stop=True)
