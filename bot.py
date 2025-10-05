import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from data_fetcher import fetch_ohlcv, get_top_coins_by_category
from analyzer import analyze_coin

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Master Trade Bot đã sẵn sàng! Gõ /analyze BTCUSDT để xem phân tích.")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Nhập mã coin, ví dụ: /analyze BTCUSDT")
        return
    symbol = context.args[0].upper()
    try:
        df = fetch_ohlcv(symbol)
        result = analyze_coin(df, symbol)
        msg = (
            f"📊 **{symbol}**\n"
            f"Giá hiện tại: {result['price']:.4f} USD\n"
            f"Xu hướng: {result['trend']}\n"
            f"Tín hiệu: {result['recommend']}\n"
            f"Lý do: {result['reason']}\n"
            f"TP: {result['tp_long']:.2f}, SL: {result['sl_long']:.2f}\n"
            f"R:R = {result['rr']:.1f}%"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analyze", analyze))

if __name__ == "__main__":
    app.run_polling()
