import time

_cache = {}

CACHE_LIFETIME = 60 * 10  # 10 phút

def cache_data(key, data):
    _cache[key] = {'data': data, 'time': time.time()}

def get_cached_data(key):
    return _cache.get(key, {}).get('data', None)

def is_cache_fresh(key):
    entry = _cache.get(key)
    if entry and (time.time() - entry['time'] >= CACHE_LIFETIME):
        _cache.pop(key, None)  # Xóa cache cũ
        return False
    return bool(entry and (time.time() - entry['time'] < CACHE_LIFETIME))
