from telegram.ext import Application, CommandHandler
from .general_handler import start_command, help_command
from .ticket_handler import get_ticket_conversation_handler

def register_handlers(app: Application):
    """
    Fungsi pendaftaran semua handler ke bot Telegram.
    Tiap membuat handler baru di folder 'handlers/', daftarkan di sini.
    """
    # 1. Handler Perintah Umum
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # 2. Handler Modul Tiket
    app.add_handler(get_ticket_conversation_handler())
