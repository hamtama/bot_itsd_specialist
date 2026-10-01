import os
import sys
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application

# Mengambil registrasi handler dari folder handlers/
from handlers import register_handlers

# 1. Load Token dari file .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 2. Siapkan Folder Logs & Logging
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, "bot.log")

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("bot")


async def error_handler(update: object, context):
    """Menangani error tak terduga agar bot tidak langsung crash."""
    logger.error("Terjadi error pada update:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Terjadi kendala teknis pada sistem saat memproses pesan Anda. Coba lagi beberapa saat lagi."
            )
        except Exception:
            pass


def main():
    if not TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN belum diatur!")
        print("💡 Silakan isi token bot Anda di dalam file .env")
        sys.exit(1)

    print("🤖 Menginisialisasi Bot Telegram...")

    # 3. Bangun Application Telegram
    app = Application.builder().token(TOKEN).build()

    # 4. Daftarkan Semua Handler dari folder handlers/
    register_handlers(app)

    # 5. Daftarkan Error Handler
    app.add_error_handler(error_handler)

    print("🚀 Bot berhasil berjalan!")
    print(f"📝 Log dicatat di: {log_file}")
    print("Tekan Ctrl+C untuk menghentikan bot.")

    # 6. Jalankan Bot (Polling)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
