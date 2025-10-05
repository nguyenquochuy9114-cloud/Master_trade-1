import os
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from data_fetcher import fetch_ohlcv
from analyzer import analyze_coin

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lấy token
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set!")

executor = ThreadPoolExecutor()

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
        loop = asyncio.get_event_loop()
        ohlcv = await loop.run_in_executor(executor, lambda: fetch_ohlcv(symbol))
        result = await loop.run_in_executor(executor, lambda: analyze_coin(ohlcv, symbol))
        if isinstance(result, (dict, list)):
            await update.message.reply_text(str(result))
        else:
            await update.message.reply_text(f"Kết quả: {result}")
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        await update.message.reply_text(f"❌ Lỗi khi phân tích: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))
    app.run_polling()

if __name__ == "__main__":
    main()
