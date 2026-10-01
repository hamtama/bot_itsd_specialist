# 🤖 Telegram Incident Bot (Clean Framework)

Framework bot telegram yang simpel, terorganisir, dan bersih:
- **`bot.py`** berada di luar (root) sebagai entry point utama.
- **`handlers/`** khusus menangani event Telegram (perintah `/start`, kirim file, tombol dsb).
- **`modules/`** khusus script logika bisnis murni data processing (`ticket_distributor.py`, dll).
- **`data/`** untuk file input/output CSV & Excel.
- **`logs/`** untuk file log aktivitas bot (`logs/bot.log`).

---

## 📁 Struktur File & Folder

```text
BOT/
│
├── bot.py                        # File utama bot (jalankan: python bot.py)
├── .env.example                  # Template token Telegram
├── requirements.txt              # Library yang dibutuhkan
├── README.md                     # Panduan penggunaan
│
├── auth/                         # Modul otentikasi / hak akses user
│
├── data/                         # Folder input / output file CSV & Excel
│
├── database/                     # Folder koneksi atau file database SQLite
│
├── handlers/                     # 📂 KHUSUS HANDLER TELEGRAM
│   ├── __init__.py               # Pendaftaran semua handler ke bot
│   ├── general_handler.py        # Handler /start, /help
│   └── ticket_handler.py         # Handler pembagian tiket incident
│
├── logs/                         # 📂 Folder log aktivitas bot
│
└── modules/                      # 📂 KHUSUS SCRIPT LOGIKA BISNIS
    ├── __init__.py
    └── ticket_distributor.py     # Script pemrosesan & pembagian tiket
```

---

## 🚀 Cara Menjalankan

1. **Buat file `.env`**:
   Salin `.env.example` menjadi `.env`, lalu isi dengan token bot Telegram dari `@BotFather`:
   ```env
   TELEGRAM_BOT_TOKEN=7123456789:AAHk_xxxxxxxxxxxxxxxxxxxx
   ```

2. **Install Library**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan Bot**:
   ```bash
   python bot.py
   ```
