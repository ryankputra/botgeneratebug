import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import base64
import json

API_TOKEN = '7911127984:AAFgJUF0mLatEqIxmpkEcaKKV3-op7nIot0'  # Ganti dengan API token Anda
bot = telebot.TeleBot(API_TOKEN)

# Dictionary untuk menyimpan link VMess sementara berdasarkan ID pengguna
user_links = {}

# Dictionary pilihan bug
bugs = {
    "xl_vidio": "quiz.int.vidio.com",
    "xl_edukasi": "172.67.73.39",
    "telkomsel_ilped": "104.26.6.171",
    "telkomsel_ilped_alt": "104.26.7.171",
    "xl_viu": "zaintest.vuclip.com",  # Bug XL viu
    "xl_vip": "104.17.3.81",
    "byu_opok": "space.byu.id" 
}

# Sambutan Selamat Datang beserta petunjuk penggunaan
def welcome_message():
    return '''
🎉 Selamat Datang di RyyStore Tools!🎉

Hai! Terima kasih telah bergabung dengan *RyyStore Tools*, tempat terbaik untuk memenuhi semua kebutuhan tools digital Anda! 
Kami menyediakan GenerateVMees&Trojan untuk mensisipkan Bug🚀💡
Bug Yang Tersedia:
- XL Vidio
- XL Edukasi
- XL VIU
- XL VIP
- TELKOMSEL ILMUPEDIA
- BYU OPOK
============================================================
============================================================
CARA MENGGUNAKAN BOT:
1. Kirim Link VMess/Trojan: Cukup kirimkan link VMess atau Trojan yang ingin Anda modifikasi.
Jika ada butuh SSH, VMess, Trojan. Bisa Beli Di @RyyVpn26 Tools! 🔥
'''

# Fungsi untuk membuat keyboard pilihan bug
def create_bug_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("XL Vidio", callback_data="bug_xl_vidio"))
    markup.add(InlineKeyboardButton("XL Edukasi", callback_data="bug_xl_edukasi"))
    markup.add(InlineKeyboardButton("Telkomsel IlmuPedia", callback_data="bug_telkomsel_ilped"))
    markup.add(InlineKeyboardButton("XL Viu", callback_data="bug_xl_viu"))  # Pilihan bug XL Viu
    markup.add(InlineKeyboardButton("XL VIP", callback_data="bug_xl_vip"))
    markup.add(InlineKeyboardButton("BYU OPOK", callback_data="bug_byu_opok")) 
    return markup

# Fungsi untuk membuat keyboard pilihan field (address atau SNI)
def create_field_keyboard(link, bug_value):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Address", callback_data=f"field_address_{bug_value}"),
               InlineKeyboardButton("SNI", callback_data=f"field_sni_{bug_value}"))
    return markup

# Fungsi untuk mengubah link VMess/Trojan dengan bug
def generate_link_with_bug(link, bug, field, is_trojan=False):
    # Memproses link Trojan atau VMess
    try:
        if is_trojan:
            # Memproses link Trojan
            # Format Trojan URL: trojan://<uuid>@<hostname>:<port>?path=<path>&security=<security>&host=<host>&type=<type>&sni=<sni>
            trojan_parts = link.split('@')
            uuid = trojan_parts[0].split('://')[1]
            host_parts = trojan_parts[1].split('?')
            hostname_port = host_parts[0].split(':')
            hostname = hostname_port[0]
            port = hostname_port[1]
            params = host_parts[1] if len(host_parts) > 1 else ""
            
            # Inisialisasi updated_params jika params tidak kosong
            updated_params = params
            
            # Ganti parameter sesuai field yang dipilih
            if field == "sni":
                updated_params = params.replace(f"sni={hostname}", f"sni={bug}")
            elif field == "address":
                hostname = bug
            updated_link = f"trojan://{uuid}@{hostname}:{port}?{updated_params}"
            return updated_link

        # Jika VMess
        vmess_data = json.loads(base64.b64decode(link[8:]).decode('utf-8'))
        if field == "address":
            vmess_data["add"] = bug
        elif field == "sni":
            vmess_data["sni"] = bug
        updated_link = "vmess://" + base64.b64encode(json.dumps(vmess_data).encode('utf-8')).decode('utf-8')
        return updated_link
    except Exception as e:
        return f"Error processing link: {e}"

# Handler untuk pesan /start (menyambut pengguna baru)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, welcome_message())

# Handler untuk pesan VMess atau Trojan
@bot.message_handler(func=lambda message: message.text.startswith("vmess://") or message.text.startswith("trojan://"))
def process_link(message):
    link = message.text
    user_links[message.from_user.id] = link  # Simpan link
    is_trojan = message.text.startswith("trojan://")  # Cek apakah itu link Trojan
    bot.send_message(message.chat.id, "Pilih bug yang ingin Anda gunakan:", reply_markup=create_bug_keyboard())

# Handler untuk memilih bug
@bot.callback_query_handler(func=lambda call: call.data.startswith("bug_"))
def handle_bug_selection(call):
    bug_key = call.data.split("_", 1)[1]
    bug_value = bugs.get(bug_key)

    # Ambil link dari penyimpanan sementara
    link = user_links.get(call.from_user.id)
    
    if link:
        # Cek apakah link adalah Trojan
        is_trojan = link.startswith("trojan://")
        bot.send_message(call.message.chat.id, "Pilih tempat untuk memasukkan bug. biasanya kebanyakan bug di tempatkan di Address:", reply_markup=create_field_keyboard(link, bug_value))
    else:
        bot.send_message(call.message.chat.id, "Kesalahan: Tidak ada link yang dikirim sebelumnya.")

# Handler untuk memilih field (address atau SNI)
@bot.callback_query_handler(func=lambda call: call.data.startswith("field_"))
def handle_field_selection(call):
    _, field, bug_value = call.data.split("_", 2)

    # Ambil link dari penyimpanan sementara
    link = user_links.get(call.from_user.id)

    if link:
        # Generate link dengan bug
        is_trojan = link.startswith("trojan://")
        updated_link = generate_link_with_bug(link, bug_value, field, is_trojan)
        
        # Kirimkan hasil link yang sudah diupdate
        bot.send_message(call.message.chat.id, f"Link berhasil dibuat:\n\n`{updated_link}`", parse_mode="Markdown")
    else:
        bot.send_message(call.message.chat.id, "Kesalahan: Tidak ada link yang tersedia.")

# Start bot polling
bot.polling()
