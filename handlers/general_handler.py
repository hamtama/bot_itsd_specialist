from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan sambutan dan petunjuk penggunaan bot."""
    welcome_text = (
        "👋 **Halo! Selamat datang di Telegram Incident Bot.**\n\n"
        "Bot ini bisa digunakan langsung di **Chat Pribadi** maupun di **Grup Tim** "
        "agar seluruh anggota tim dapat melihat hasil pemrosesan data secara bersamaan.\n\n"
        "📌 **Fitur Distribusi Tiket:**\n"
        "• **Mode Cepat (Paling Praktis di Grup):**\n"
        "  Kirim file CSV/Excel dengan caption daftar nama agent (contoh: `Budi, Siti, Joko`).\n\n"
        "• **Mode Interaktif:**\n"
        "  Ketik perintah /distribusi atau kirim file tanpa caption, lalu ikuti tombol petunjuk bot.\n\n"
        "Ketik /help untuk melihat panduan lengkap."
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan daftar perintah bot."""
    help_text = (
        "📖 **Daftar Perintah:**\n\n"
        "• /start - Memulai bot & melihat panduan\n"
        "• /help - Menampilkan panduan ini\n"
        "• /distribusi - Memulai sesi pembagian tiket incident\n"
        "• /batal - Membatalkan sesi yang sedang aktif\n\n"
        "💡 *Tips:* Pastikan Group Privacy di BotFather di-disable agar bot bisa membaca file di grup tim."
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
