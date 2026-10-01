import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Mengambil langsung logika pemrosesan dari folder modules!
from modules.ticket_distributor import distribute_tickets

logger = logging.getLogger(__name__)

STATE_WAIT_NAMES = 1
STATE_WAIT_MODE = 2
STATE_WAIT_FIXED_COUNT = 3

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani pengiriman file CSV atau Excel."""
    message = update.message
    doc = message.document

    if not (doc.file_name.lower().endswith(".csv") or doc.file_name.lower().endswith((".xlsx", ".xls"))):
        await message.reply_text("⚠️ Mohon kirimkan file berekstensi **.csv**, **.xlsx**, atau **.xls**.", parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END

    status_msg = await message.reply_text("⏳ Sedang mengunduh dan membaca file...")

    try:
        tg_file = await context.bot.get_file(doc.file_id)
        input_path = os.path.join(DATA_DIR, f"input_{doc.file_name}")
        await tg_file.download_to_drive(input_path)
    except Exception as e:
        logger.error(f"Gagal download file: {e}")
        await status_msg.edit_text("❌ Gagal mengunduh file dari Telegram. Silakan coba kembali.")
        return ConversationHandler.END

    caption = message.caption.strip() if message.caption else ""

    # MODE CEPAT: Menggunakan caption nama agent
    if caption:
        names_text = caption
        if names_text.lower().startswith(("/distribusi", "/bagi")):
            parts = names_text.split(" ", 1)
            names_text = parts[1] if len(parts) > 1 else ""

        if names_text:
            await status_msg.edit_text("⚙️ Memproses pembagian tiket secara merata...")
            await process_and_send_result(
                update=update,
                context=context,
                file_path=input_path,
                names_input=names_text,
                mode="equal",
                status_msg=status_msg
            )
            return ConversationHandler.END

    # MODE INTERAKTIF: Panduan bertahap
    context.user_data["input_file_path"] = input_path
    context.user_data["file_name"] = doc.file_name

    await status_msg.edit_text(
        f"✅ File **{doc.file_name}** berhasil diterima!\n\n"
        "Silakan balas pesan ini dengan **daftar nama agent** (pisahkan tanda koma).\n\n"
        "*Contoh: Budi, Siti, Joko, Andi*\n"
        "*(Ketik /batal untuk membatalkan)*",
        parse_mode=ParseMode.MARKDOWN
    )
    return STATE_WAIT_NAMES


async def start_distribusi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler jika user mengetik perintah /distribusi lebih dulu."""
    await update.message.reply_text(
        "📂 Silakan kirimkan file **CSV** atau **Excel** tiket Anda.\n"
        "*(Ketik /batal jika ingin membatalkan)*",
        parse_mode=ParseMode.MARKDOWN
    )
    return STATE_WAIT_NAMES


async def receive_agent_names(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menerima teks nama-nama agent."""
    raw_names = update.message.text.strip()
    if not raw_names:
        await update.message.reply_text("⚠️ Nama agent tidak boleh kosong. Silakan ketik kembali:")
        return STATE_WAIT_NAMES

    context.user_data["names_input"] = raw_names

    keyboard = [
        [
            InlineKeyboardButton("⚖️ Bagi Rata (Equal)", callback_data="mode_equal"),
            InlineKeyboardButton("🎯 Jumlah Tetap (Fixed)", callback_data="mode_fixed"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👥 Agent yang didaftarkan:\n`{raw_names}`\n\n"
        "Pilih metode pembagian tiket:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    return STATE_WAIT_MODE


async def handle_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani respon tombol mode."""
    query = update.callback_query
    await query.answer()

    choice = query.data

    if choice == "mode_equal":
        await query.edit_message_text("⚙️ Mendistribusikan tiket secara merata...")
        file_path = context.user_data.get("input_file_path")
        names_input = context.user_data.get("names_input")

        await process_and_send_result(
            update=update,
            context=context,
            file_path=file_path,
            names_input=names_input,
            mode="equal",
            status_msg=query.message
        )
        return ConversationHandler.END

    elif choice == "mode_fixed":
        await query.edit_message_text(
            "🔢 Berapa tiket per agent?\n"
            "Kirimkan angkanya saja (Contoh: `5` atau `10`):",
            parse_mode=ParseMode.MARKDOWN
        )
        return STATE_WAIT_FIXED_COUNT


async def receive_fixed_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menerima angka untuk mode fixed."""
    text = update.message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await update.message.reply_text("⚠️ Masukkan angka bulat positif (misal: 5, 10).")
        return STATE_WAIT_FIXED_COUNT

    count = int(text)
    file_path = context.user_data.get("input_file_path")
    names_input = context.user_data.get("names_input")

    status_msg = await update.message.reply_text(f"⚙️ Memproses alokasi {count} tiket per agent...")

    await process_and_send_result(
        update=update,
        context=context,
        file_path=file_path,
        names_input=names_input,
        mode="fixed",
        tickets_per_person=count,
        status_msg=status_msg
    )
    return ConversationHandler.END


async def process_and_send_result(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    file_path: str,
    names_input: str,
    mode: str,
    tickets_per_person: int = None,
    status_msg = None
):
    """Menjalankan modul dan mengirim hasil ke chat/grup."""
    chat_id = update.effective_chat.id

    out_csv, summary, err = distribute_tickets(
        file_path=file_path,
        names_input=names_input,
        mode=mode,
        tickets_per_person=tickets_per_person,
        output_dir=DATA_DIR
    )

    if err:
        error_text = f"❌ **Gagal Memproses Tiket:**\n{err}"
        if status_msg:
            await status_msg.edit_text(error_text, parse_mode=ParseMode.MARKDOWN)
        else:
            await context.bot.send_message(chat_id=chat_id, text=error_text, parse_mode=ParseMode.MARKDOWN)
        return

    total_distributed = sum(summary.values())
    summary_lines = [
        "📊 **HASIL DISTRIBUSI TIKET**",
        "━━━━━━━━━━━━━━━━━━━━━━",
        f"⚙️ **Mode:** {mode.upper()}" + (f" ({tickets_per_person} tiket/orang)" if mode == 'fixed' else " (Merata)"),
        f"📦 **Total Tiket:** {total_distributed}",
        "━━━━━━━━━━━━━━━━━━━━━━"
    ]

    for name, cnt in summary.items():
        if name == "SISA TIKET":
            summary_lines.append(f"⚠️ **{name}**: {cnt} tiket (belum terbagi)")
        else:
            summary_lines.append(f"👤 **{name}**: {cnt} tiket")

    summary_lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    summary_lines.append("📁 File query CSV hasil terlampir di bawah:")
    report_caption = "\n".join(summary_lines)

    try:
        if status_msg:
            await status_msg.delete()
    except Exception:
        pass

    with open(out_csv, "rb") as f:
        await context.bot.send_document(
            chat_id=chat_id,
            document=f,
            filename=os.path.basename(out_csv),
            caption=report_caption,
            parse_mode=ParseMode.MARKDOWN
        )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Membatalkan sesi."""
    context.user_data.clear()
    await update.message.reply_text("🚫 Sesi pembagian tiket dibatalkan.")
    return ConversationHandler.END


def get_ticket_conversation_handler():
    """Mengembalikan ConversationHandler untuk bot."""
    return ConversationHandler(
        entry_points=[
            CommandHandler("distribusi", start_distribusi_command),
            MessageHandler(filters.Document.ALL, handle_document)
        ],
        states={
            STATE_WAIT_NAMES: [
                MessageHandler(filters.Document.ALL, handle_document),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_agent_names)
            ],
            STATE_WAIT_MODE: [
                CallbackQueryHandler(handle_mode_callback)
            ],
            STATE_WAIT_FIXED_COUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_fixed_count)
            ],
        },
        fallbacks=[CommandHandler("batal", cancel_command)],
        per_chat=True,
        per_user=False
    )
