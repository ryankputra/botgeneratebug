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
sudo nano /etc/systemd/system/bugbot.service
```
ISI
```
[Unit]
Description=Bug Bot Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /root/botgeneratebug/bot.py
Restart=always
User=root
WorkingDirectory=/root/botgeneratebug

[Install]
WantedBy=multi-user.target

```
Jalankan
```
sudo systemctl daemon-reload
sudo systemctl start bugbot 
sudo systemctl enable bugbot
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
