import matplotlib.pyplot as plt
import mplfinance as mpf

def plot_candlestick(df, symbol, ema12, ema26):
    df = df.set_index('timestamp')
    df.index.name = 'Date'
    fig, ax = plt.subplots(figsize=(8,4))
    mpf.plot(df, type='candle', ax=ax)
    path = f"{symbol}_chart.png"
    plt.savefig(path)
    plt.close()
    return path
