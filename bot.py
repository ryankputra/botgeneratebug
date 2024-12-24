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

def create_bug_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("XL Vidio", callback_data="bug_xl_vidio"),
               InlineKeyboardButton("XL Edukasi", callback_data="bug_xl_edukasi"))
    markup.row(InlineKeyboardButton("Telkomsel IlmuPedia", callback_data="bug_telkomsel_ilped"))
    markup.row(InlineKeyboardButton("XL Viu", callback_data="bug_xl_viu"),
               InlineKeyboardButton("XL VIP", callback_data="bug_xl_vip"))
    markup.row(InlineKeyboardButton("BYU OPOK", callback_data="bug_byu_opok"))
    markup.row(InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu"))
    return markup

def create_telkomsel_ilped_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Telkomsel IlmuPedia Bug 1", callback_data="bug_telkomsel_ilped"),
        InlineKeyboardButton("Telkomsel IlmuPedia Bug 2 (rekomended)", callback_data="bug_telkomsel_ilped_alt")
    )
    markup.row(InlineKeyboardButton("🔙 Kembali", callback_data="menu_vmess"))
    return markup

def create_field_keyboard(bug_value):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Address", callback_data=f"field_address_{bug_value}"),
        InlineKeyboardButton("SNI", callback_data=f"field_sni_{bug_value}")
    )
    markup.row(InlineKeyboardButton("🔙 Kembali", callback_data="menu_vmess"))
    return markup

def generate_link_with_bug(link, bug, field, is_trojan=False):
    try:
        if is_trojan:
            trojan_parts = link.split('@')
            uuid = trojan_parts[0].split('://')[1]
            host_parts = trojan_parts[1].split('?')
            hostname_port = host_parts[0].split(':')
            hostname = hostname_port[0]
            port = hostname_port[1]
            params = host_parts[1] if len(host_parts) > 1 else ""
            
            updated_params = params
            if field == "sni":
                updated_params = params.replace(f"sni={hostname}", f"sni={bug}")
            elif field == "address":
                hostname = bug
            return f"trojan://{uuid}@{hostname}:{port}?{updated_params}"

        vmess_data = json.loads(base64.b64decode(link[8:]).decode('utf-8'))
        if field == "address":
            vmess_data["add"] = bug
        elif field == "sni":
            vmess_data["sni"] = bug
        return "vmess://" + base64.b64encode(json.dumps(vmess_data).encode('utf-8')).decode('utf-8')
    except Exception as e:
        return f"Error processing link: {e}"

@bot.message_handler(commands=['generate'])
def send_welcome(message):
    # Menyimpan informasi pengguna
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
    
    # Mengirim dalam beberapa pesan jika terlalu panjang
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

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "menu_vmess":
        bot.edit_message_text(
            "Silakan kirim link VMess atau Trojan Anda untuk dimodifikasi. Gausah bingung, kirimkan link mentahan yang sudah kamu copy!",
            call.message.chat.id,
            call.message.message_id,
          
        )
    
    elif call.data == "menu_otp":
        bot.edit_message_text(
            "Silakan kirim secret key 2FA Anda untuk generate OTP.",
            call.message.chat.id,
            call.message.message_id
        )
    
    elif call.data == "menu_help":
        help_text = """
 Panduan Penggunaan RyyStore Tools

1. Generate VMess/Trojan:
   • Kirim link VMess/Trojan Anda
   • Pilih jenis bug yang ingin digunakan
   • Pilih lokasi bug (Address/SNI)
   • Bot akan mengirim link yang sudah dimodifikasi

2. Generate OTP:
   • Kirim secret key 2FA Anda
   • Bot akan generate kode OTP
   • Gunakan tombol Copy untuk menyalin OTP

Untuk bantuan lebih lanjut, hubungi @RyyVpn26
        """
        bot.edit_message_text(
            help_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    
    elif call.data == "kembali":
        bot.edit_message_text(
            welcome_message(),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu_keyboard()
        )
    
    elif call.data.startswith("bug_"):
        bug_key = call.data.split("_", 1)[1]
        bug_value = bugs.get(bug_key)
        if bug_value:
            bot.edit_message_text(
                "Pilih lokasi untuk memasukkan bug. kebanyakan bug berada di Address:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_field_keyboard(bug_value)
            )
    
    elif call.data.startswith("field_"):
        _, field, bug_value = call.data.split("_", 2)
        link = user_links.get(call.from_user.id)
        if link:
            is_trojan = link.startswith("trojan://")
            updated_link = generate_link_with_bug(link, bug_value, field, is_trojan)
            bot.send_message(
                call.message.chat.id,
                f"✅ Link berhasil dibuat:\n\n`{updated_link}`",
                parse_mode="Markdown",
                reply_markup=main_menu_keyboard()
            )

@bot.message_handler(func=lambda message: message.text.startswith(("vmess://", "trojan://")))
def handle_link(message):
    user_links[message.from_user.id] = message.text
    bot.reply_to(
        message,
        "Link diterima! Silakan pilih jenis bug:",
        reply_markup=create_bug_keyboard()
    )

@bot.message_handler(func=lambda message: len(message.text) > 10 and not message.text.startswith(("/", "vmess://", "trojan://")))
def handle_secret(message):
    try:
        secret = message.text.strip()
        user_secrets[message.from_user.id] = secret
        totp = pyotp.TOTP(secret)
        otp = totp.now()
        
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📋 Copy OTP", callback_data=f"copy_{otp}"),
            InlineKeyboardButton("🔙 Menu Utama", callback_data="back_to_menu")
        )
        
        bot.reply_to(
            message,
            f"🔐 OTP Anda:\n\n`{otp}`",
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception as e:
        bot.reply_to(message, "❌ Secret key tidak valid. Mohon periksa kembali.")

@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.text.startswith("/broadcast"))
def handle_broadcast(message):
    broadcast_message = message.text.replace("/broadcast", "").strip()
    if broadcast_message:
        for user_id in active_users:
            try:
                bot.send_message(user_id, f"📢 *Pesan Dari Admin @RyyVpn26*:\n\n{broadcast_message}", parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Failed to send broadcast to {user_id}: {e}")
        bot.reply_to(message, "✅ Broadcast selesai dikirim.")
    else:
        bot.reply_to(message, "❌ Mohon sertakan pesan broadcast.")

# Start bot
print("Bot started...")
bot.polling(none_stop=True)
