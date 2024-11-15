install dulu
```
sudo apt install python3-pip
```

```
pip3 install pyTelegramBotAPI
```
```
git clone https://github.com/ryankputra/botgeneratebug.git
```
```
cd botgeneratebug
```

jalankan bot di vps dengan
```
python3 bot.py
```
setup agar bot jalan di vps tanpa henti
```
sudo apt install screen
```
```
screen
```
```
python3 bot.py
```


running menggunakan systemd
```
sudo nano /etc/systemd/system/telegrambot.service
```
ISI
```
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/botgeneratebug
ExecStart=/usr/bin/python3 /path/to/botgeneratebug/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
Jalankan
```
# Reload daemon
sudo systemctl daemon-reload

# Start bot
sudo systemctl start bugbot

# Enable autostart saat reboot
sudo systemctl enable bugbot

# Cek status bot
sudo systemctl status bugbot
```
cek apakah bot berjalan
```
# Cek proses
ps aux | grep python3

# Cek log
tail -f /var/log/syslog | grep bugbot
```
```
rm -rf botgeneratebug
```
