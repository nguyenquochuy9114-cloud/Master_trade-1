import requests
import pandas as pd
import time
from database import cache_data, get_cached_data, is_cache_fresh
from requests.exceptions import RequestException

def fetch_ohlcv(coin_symbol, interval='1h', limit=100, source_priority=['binance', 'okx', 'coingecko']):
    coin_id = coin_symbol.lower()
    if is_cache_fresh(coin_id):
        cached = get_cached_data(coin_id)
        if cached:
            return pd.DataFrame(cached)

    for source in source_priority:
        try:
            if source == 'binance':
                url = f"https://api.binance.com/api/v3/klines?symbol={coin_symbol}&interval={interval}&limit={limit}"
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                if resp.status_code == 200:
                    data = resp.json()
                    df = pd.DataFrame(data, columns=['timestamp','open','high','low','close','volume','_','_','_','_','_','_'])
                    df = df[['timestamp','open','high','low','close','volume']].replace('', pd.NA).dropna().astype(float)
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    if not df.empty:
                        cache_data(coin_id, df.to_dict('records'))
                        return df
            elif source == 'okx':
                url = f"https://www.okx.com/api/v5/market/candles?instId={coin_symbol}&bar={interval}&limit={limit}"
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                if resp.status_code == 200:
                    data = resp.json()['data']
                    if data:
                        df = pd.DataFrame(data, columns=['timestamp','open','high','low','close','volume','_'])
                        df = df[['timestamp','open','high','low','close','volume']].replace('', pd.NA).dropna().astype(float)
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        df = df[::-1]
                        if not df.empty:
                            cache_data(coin_id, df.to_dict('records'))
                            return df
            elif source == 'coingecko':
                coin_id = coin_symbol.lower().replace('usdt', '')
                url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days=30"
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                if resp.status_code == 200:
                    data = resp.json()
                    df = pd.DataFrame(data, columns=['timestamp','open','high','low','close'])
                    df['volume'] = df['close'] * 0  # Giả lập volume
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df = df.sort_values('timestamp')
                    if not df.empty:
                        cache_data(coin_id, df.to_dict('records'))
                        return df
        except RequestException as e:
            if resp.status_code == 429:
                time.sleep(60)  # Chờ 1 phút nếu rate limit
                continue
            print(f"Error with {source}: {e}")
            continue
        time.sleep(1)  # Delay giữa các source

    raise ValueError(f"Failed to fetch data for {coin_symbol} from all sources")

def get_top_coins_by_category(category, per_page=50):
    categories_map = {
        'top': 'all',
        'meme': 'meme-token',
        'defi': 'decentralized-finance-defi',
        'ai': 'ai-agents'
    }
    cat_id = categories_map.get(category, 'all')
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category={cat_id}&order=market_cap_desc&per_page={per_page}&page=1&sparkline=false"
    resp = requests.get(url, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    return []

def get_long_short_ratio(symbol):
    try:
        url = f"https://fapi.binance.com/fapi/v1/globalLongShortAccountRatio?symbol={symbol}&period=5m&limit=1"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        if resp.status_code == 200:
            data = resp.json()[0]
            return float(data['longShortRatio'])
    except Exception:
        pass
    return 1.0
