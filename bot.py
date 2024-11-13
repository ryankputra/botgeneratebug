import json
import base64
import pyotp
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

API_TOKEN = "7307313664:AAHnWmKaaOew8cBFGbOTu2ipfQQ8M_twL0U"
ADMIN_ID = 6583386476  # Ganti dengan ID admin
bot = TeleBot(API_TOKEN)

# Menyimpan ID pengguna aktif yang menggunakan bot
active_users = set()
user_links = {}
user_secrets = {}
bugs = {
    # Tambahkan bugs yang sesuai
}

def welcome_message():
    return "Selamat datang di RyyStore Tools!"

def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        welcome_message(),
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )
    active_users.add(message.from_user.id)  # Menambahkan ID pengguna ke daftar active_users

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "menu_vmess":
        bot.edit_message_text(
            "Silakan kirim link VMess atau Trojan Anda untuk dimodifikasi.",
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

# Fitur baru untuk menampilkan statistik pengguna bot (khusus admin)
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.text == "/user_stats")
def handle_user_stats(message):
    user_count = len(active_users)
    user_list = "\n".join([str(user_id) for user_id in active_users])
    response = f"📊 *Statistik Pengguna Bot*\n\nTotal Pengguna: {user_count}\n\nDaftar Pengguna:\n{user_list}"
    bot.reply_to(message, response, parse_mode="Markdown")

# Perintah broadcast untuk mengirim pesan ke semua pengguna (khusus admin)
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
