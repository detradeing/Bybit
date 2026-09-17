import json
import os
import time
from src.config import STATE_FILE, HISTORY_FILE, LOOKBACK_HOURS


def _load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_state():
    # ساختار: {"open_position": null | {...جزئیات پوزیشن باز...}}
    return _load(STATE_FILE, {"open_position": None})


def save_state(state):
    _save(STATE_FILE, state)


def load_history():
    # لیستی از {"t": timestamp, "price": float}
    return _load(HISTORY_FILE, [])


def append_price(price):
    history = load_history()
    now = time.time()
    history.append({"t": now, "price": price})
    cutoff = now - LOOKBACK_HOURS * 3600
    history = [h for h in history if h["t"] >= cutoff]
    _save(HISTORY_FILE, history)
    return history


def max_price_in_window(history, exclude_last=True):
    """بیشینه قیمت طی بازه لوک‌بک، بدون احتساب آخرین نقطه (قیمت لحظه فعلی)."""
    points = history[:-1] if exclude_last and history else history
    if not points:
        return None
    return max(p["price"] for p in points)


def last_price_before_current(history):
    """آخرین قیمت ثبت‌شده قبل از نقطه فعلی (برای تشخیص جهت حرکت)."""
    if len(history) < 2:
        return None
    return history[-2]["price"]
