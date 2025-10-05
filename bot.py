import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from data_fetcher import fetch_ohlcv
from analyzer import analyze_coin

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Master Trade Bot đã sẵn sàng!\nGõ /analyze BTCUSDT để xem phân tích."
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Vui lòng nhập mã coin. Ví dụ: /analyze BTCUSDT")
        return

    symbol = context.args[0].upper()
    await update.message.reply_text(f"🔍 Đang phân tích {symbol} ...")

    try:
        ohlcv = fetch_ohlcv(symbol)
        result = analyze_coin(ohlcv, symbol)
        await update.message.reply_text(str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi phân tích: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))
    app.run_polling()

if __name__ == "__main__":
    main()
