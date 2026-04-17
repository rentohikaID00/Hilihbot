import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8544556604:AAEGfme74pm84ZrFJEhlHHk-DCnhndsEhf4"
API_KEY = "b47d4fd8e77051a3766505f7ade3d5b0"
BASE_URL = "https://api.jasaotp.id/v2"

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Halo! Bot OTP siap digunakan!\n\n"
        "📌 Perintah:\n"
        "/saldo - Cek saldo\n"
        "/negara - Daftar negara\n"
        "/operator <id_negara> - Daftar operator\n"
        "/layanan <id_negara> - Daftar layanan & harga\n"
        "/order <id_negara> <layanan> <operator> - Pesan OTP\n"
        "Contoh: /order 6 wa any\n\n"
        "/cek <id_order> - Cek OTP masuk\n"
        "/batal <id_order> - Batalkan order"
    )
    await update.message.reply_text(text)

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
            text += f"ID {n['id_negara']} - {n['nama_negara']}\n"
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
        ops = data["data"].get(negara_id, [])
        text = f"📡 Operator negara {negara_id}:\n" + "\n".join(ops)
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
    layanan_data = data.get(negara_id, {})
    if layanan_data:
        text = f"📋 Layanan negara {negara_id}:\n"
        for kode, info in layanan_data.items():
            text += f"{kode} - {info['layanan']} | Rp{info['harga']} | Stok: {info['stok']}\n"
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("❌ Gagal ambil layanan!")

# Order OTP
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("⚠️ Format: /order <id_negara> <layanan> <operator>\nContoh: /order 6 wa any")
        return
    negara_id = context.args[0]
    layanan_kode = context.args[1]
    operator_nama = context.args[2]
    r = requests.get(f"{BASE_URL}/order.php?api_key={API_KEY}&negara={negara_id}&layanan={layanan_kode}&operator={operator_nama}")
    data = r.json()
    if data["success"]:
        text = (
            f"✅ Order berhasil!\n"
            f"📱 Nomor: {data['data']['number']}\n"
            f"🆔 ID Order: {data['data']['order_id']}\n\n"
            f"Gunakan /cek {data['data']['order_id']} untuk cek OTP"
        )
        await update.message.reply_text(text)
    else:
        await update.message.reply_text(f"❌ Gagal order: {data['message']}")

# Cek OTP
async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Format: /cek <id_order>\nContoh: /cek 1728868")
        return
    order_id = context.args[0]
    r = requests.get(f"{BASE_URL}/sms.php?api_key={API_KEY}&id={order_id}")
    data = r.json()
    if data["success"]:
        await update.message.reply_text(f"📩 OTP kamu: {data['data']['otp']}")
    else:
        await update.message.reply_text(f"⏳ OTP belum masuk, coba lagi!")

# Batalkan Order
async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Format: /batal <id_order>\nContoh: /batal 1728868")
        return
    order_id = context.args[0]
    r = requests.get(f"{BASE_URL}/cancel.php?api_key={API_KEY}&id={order_id}")
    data = r.json()
    if data["success"]:
        refund = data["data"]["refunded_amount"]
        await update.message.reply_text(f"✅ Order dibatalkan!\n💰 Refund: Rp{refund}")
    else:
        await update.message.reply_text(f"❌ Gagal batal: {data['message']}")

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
