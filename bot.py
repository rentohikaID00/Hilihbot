import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8544556604:AAEGfme74pm84ZrFJEhlHHk-DCnhndsEhf4"
API_KEY = "b47d4fd8e77051a3766505f7ade3d5b0"
BASE_URL = "https://api.jasaotp.id/v2"

# Cek Saldo
async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = requests.get(f"{BASE_URL}/balance.php?api_key={API_KEY}")
    data = r.json()
    if data["success"]:
        await update.message.reply_text(f"💰 Saldo kamu: Rp{data['data']['saldo']}")
    else:
        await update.message.reply_text("❌ Gagal cek saldo!")

# Daftar Negara
async def negara(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = requests.get(f"{BASE_URL}/negara.php")
    data = r.json()
    if data["success"]:
        text = "🌍 Daftar Negara:\n"
        for n in data["data"]:
            text += f"{n['id_negara']} - {n['nama_negara']}\n"
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("❌ Gagal ambil data negara!")

# Daftar Operator
async def operator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Format: /operator <id_negara>\nContoh: /operator 6")
        return
    negara_id = context.args[0]
    r = requests.get(f"{BASE_URL}/operator.php?negara={negara_id}")
    data = r.json()
    if data["success"]:
        text = f"📡 Operator negara {negara_id}:\n"
        for o in data["data"]:
            text += f"{o['id_operator']} - {o['nama_operator']}\n"
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("❌ Gagal ambil operator!")

# Daftar Layanan
async def layanan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Format: /layanan <id_negara>\nContoh: /layanan 6")
        return
    negara_id = context.args[0]
    r = requests.get(f"{BASE_URL}/layanan.php?negara={negara_id}")
    data = r.json()
    if data["success"]:
        text = f"📋 Layanan negara {negara_id}:\n"
        for l in data["data"]:
            text += f"{l['id_layanan']} - {l['nama_layanan']}\n"
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("❌ Gagal ambil layanan!")

# Order OTP
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Format: /order <id_negara> <id_layanan>\nContoh: /order 6 1")
        return
    negara_id = context.args[0]
    layanan_id = context.args[1]
    r = requests.get(f"{BASE_URL}/order.php?api_key={API_KEY}&negara={negara_id}&layanan={layanan_id}")
    data = r.json()
    if data["success"]:
        text = (
            f"✅ Order berhasil!\n"
            f"📱 Nomor: {data['data']['nomor']}\n"
            f"🆔 ID Order: {data['data']['id_order']}"
        )
        await update.message.reply_text(text)
    else:
        await update.message.reply_text(f"❌ Gagal order: {data['message']}")

# Cek OTP
async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Format: /cek <id_order>\nContoh: /cek 12345")
        return
    order_id = context.args[0]
    r = requests.get(f"{BASE_URL}/sms.php?api_key={API_KEY}&id_order={order_id}")
    data = r.json()
    if data["success"]:
        text = (
            f"📩 OTP kamu:\n"
            f"Kode: {data['data']['otp']}\n"
            f"SMS: {data['data']['sms']}"
        )
        await update.message.reply_text(text)
    else:
        await update.message.reply_text(f"⏳ OTP belum masuk: {data['message']}")

# Batalkan Order
async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Format: /batal <id_order>\nContoh: /batal 12345")
        return
    order_id = context.args[0]
    r = requests.get(f"{BASE_URL}/cancel.php?api_key={API_KEY}&id_order={order_id}")
    data = r.json()
    if data["success"]:
        await update.message.reply_text("✅ Order berhasil dibatalkan & saldo dikembalikan!")
    else:
        await update.message.reply_text(f"❌ Gagal batal: {data['message']}")

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Halo! Bot OTP siap digunakan!\n\n"
        "📌 Perintah:\n"
        "/saldo - Cek saldo\n"
        "/negara - Daftar negara\n"
        "/operator <id> - Daftar operator\n"
        "/layanan <id> - Daftar layanan\n"
        "/order <negara> <layanan> - Pesan OTP\n"
        "/cek <id_order> - Cek OTP\n"
        "/batal <id_order> - Batalkan order"
    )
    await update.message.reply_text(text)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("saldo", saldo))
app.add_handler(CommandHandler("negara", negara))
app.add_handler(CommandHandler("operator", operator))
app.add_handler(CommandHandler("layanan", layanan))
app.add_handler(CommandHandler("order", order))
app.add_handler(CommandHandler("cek", cek))
app.add_handler(CommandHandler("batal", batal))
app.run_polling()
