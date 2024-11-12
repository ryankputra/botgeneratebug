import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7911127984:AAFgJUF0mLatEqIxmpkEcaKKV3-op7nIot0'  # Ganti dengan API token Anda
bot = telebot.TeleBot(API_TOKEN)

# Dictionary untuk menyimpan link VMess sementara berdasarkan ID pengguna
user_vmess_links = {}

# Dictionary pilihan bug
bugs = {
    "xl_vidio": "quiz.int.vidio.com",
    "xl_edukasi": "172.67.73.39",
    "telkomsel_ilped": "104.26.6.171",
    "telkomsel_ilped_alt": "104.26.7.171"
}

# Sambutan Selamat Datang beserta petunjuk penggunaan
def welcome_message():
    return '''
🎉 **Selamat Datang di RyyStore Tools!** 🎉

Hai! Terima kasih telah bergabung dengan *RyyStore Tools*, tempat terbaik untuk memenuhi semua kebutuhan tools digital Anda! 🎈

Di sini, kami menyediakan berbagai layanan yang praktis dan mudah diakses. Mulai dari pembuatan akun VPN, konfigurasi jaringan, hingga optimasi tools lainnya—semuanya siap membantu meningkatkan pengalaman Anda. 🚀💡

📌 **Apa yang Bisa Anda Harapkan di RyyStore Tools?**
- **Layanan Cepat**: Respon cepat untuk semua kebutuhan Anda!
- **Keamanan Terjamin**: Data dan privasi Anda selalu menjadi prioritas kami.
- **Kemudahan Akses**: Layanan dengan panduan mudah dan langkah yang jelas.

---

**Cara Menggunakan Bot:**
1. **Kirim Link VMess/Trojan**: Cukup kirimkan link VMess atau Trojan yang ingin Anda modifikasi.
2. **Pilih Bug**: Bot akan meminta Anda memilih bug yang ingin diterapkan (misalnya, XL Vidio, Telkomsel Edukasi, atau IlmuPedia).
3. **Pilih Lokasi Bug**: Anda bisa memilih apakah bug akan dimasukkan di bagian *Address* atau *SNI* pada link.
4. **Hasilkan Link Baru**: Setelah memilih bug dan lokasinya, bot akan menghasilkan link VMess/Trojan yang telah diperbarui dengan bug yang dipilih.

Jika ada yang bisa kami bantu, jangan ragu untuk bertanya. Kami di sini untuk memastikan Anda mendapatkan yang terbaik dari layanan kami. Selamat menikmati pengalaman bersama *RyyStore Tools*! 🔥
'''

# Fungsi untuk membuat keyboard pilihan bug
def create_bug_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("XL Vidio", callback_data="bug_xl_vidio"))
    markup.add(InlineKeyboardButton("XL Edukasi", callback_data="bug_xl_edukasi"))
    markup.add(InlineKeyboardButton("Telkomsel IlmuPedia", callback_data="bug_telkomsel_ilped"))
    return markup

# Fungsi untuk membuat keyboard pilihan field (address atau SNI)
def create_field_keyboard(vmess_link, bug_value):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Address", callback_data=f"field_address_{bug_value}"),
               InlineKeyboardButton("SNI", callback_data=f"field_sni_{bug_value}"))
    return markup

# Fungsi untuk mengubah link VMess dengan bug
def generate_vmess_with_bug(vmess_link, bug, field):
    import base64
    import json

    # Decode link VMess
    try:
        vmess_data = json.loads(base64.b64decode(vmess_link[8:]).decode('utf-8'))
    except Exception as e:
        return f"Error decoding VMess link: {e}"

    # Update field
    if field == "address":
        vmess_data["add"] = bug
    elif field == "sni":
        vmess_data["sni"] = bug

    # Encode kembali link VMess
    updated_link = "vmess://" + base64.b64encode(json.dumps(vmess_data).encode('utf-8')).decode('utf-8')
    return updated_link

# Handler untuk pesan /start (menyambut pengguna baru)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, welcome_message())

# Handler untuk pesan VMess
@bot.message_handler(func=lambda message: message.text.startswith("vmess://"))
def process_vmess_link(message):
    vmess_link = message.text
    user_vmess_links[message.from_user.id] = vmess_link  # Simpan link VMess
    bot.send_message(message.chat.id, "Pilih bug yang ingin Anda gunakan:", reply_markup=create_bug_keyboard())

# Handler untuk memilih bug
@bot.callback_query_handler(func=lambda call: call.data.startswith("bug_"))
def handle_bug_selection(call):
    bug_key = call.data.split("_", 1)[1]
    bug_value = bugs.get(bug_key)

    # Ambil link VMess dari penyimpanan sementara
    vmess_link = user_vmess_links.get(call.from_user.id)
    
    if vmess_link:
        bot.send_message(call.message.chat.id, "Pilih tempat untuk memasukkan bug:", reply_markup=create_field_keyboard(vmess_link, bug_value))
    else:
        bot.send_message(call.message.chat.id, "Kesalahan: Tidak ada pesan link VMess yang dikirim sebelumnya.")

# Handler untuk memilih field (address atau SNI)
@bot.callback_query_handler(func=lambda call: call.data.startswith("field_"))
def handle_field_selection(call):
    _, field, bug_value = call.data.split("_", 2)

    # Ambil link VMess dari penyimpanan sementara
    vmess_link = user_vmess_links.get(call.from_user.id)

    if vmess_link:
        # Generate link VMess dengan bug
        updated_link = generate_vmess_with_bug(vmess_link, bug_value, field)
        
        # Kirimkan hasil link VMess yang sudah diupdate
        bot.send_message(call.message.chat.id, f"Link VMess berhasil dibuat:\n\n`{updated_link}`", parse_mode="Markdown")
    else:
        bot.send_message(call.message.chat.id, "Kesalahan: Tidak ada link VMess yang tersedia.")

# Start bot polling
bot.polling()
