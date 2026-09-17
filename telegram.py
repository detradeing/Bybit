import requests
from datetime import datetime, timezone
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }, timeout=15)


def _fmt(ts_ms):
    return datetime.fromtimestamp(int(ts_ms) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _fmt_epoch(ts_sec):
    return datetime.fromtimestamp(ts_sec, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def notify_open(symbol, entry_price, qty, leverage, tp, sl, level):
    send_message(
        f"🟢 معامله باز شد\n\n"
        f"نماد: {symbol}\n"
        f"جهت: Long\n"
        f"قیمت ورود: {entry_price}\n"
        f"حجم: {qty}\n"
        f"اهرم: {leverage}x (Isolated)\n"
        f"🎯 TP: {tp}\n"
        f"🛑 SL: {sl}\n"
        f"📌 سیگنال: رسیدن به سطح رند {level} از پایین"
    )


def notify_closed(symbol, entry_price, exit_price, qty, leverage,
                   entry_time_ts, exit_time_ts, order_id,
                   balance_before, balance_after, level):
    """
    گزارش کامل بسته‌شدن معامله.
    توجه: چون get_closed_pnl روی حساب دمو بای‌بیت پشتیبانی نمی‌شود، این تابع
    از قیمت خروجِ گرفته‌شده با get_executions + اختلاف موجودی کیف‌پول (قبل/بعد)
    برای محاسبه سود/ضرر استفاده می‌کند، نه از خودِ closedPnl صرافی.
    """
    pnl = balance_after - balance_before
    pnl_pct = (pnl / balance_before * 100) if balance_before else 0
    reason = "TP فعال شد" if pnl > 0 else "SL فعال شد"

    duration_sec = exit_time_ts - entry_time_ts
    h, rem = divmod(int(max(duration_sec, 0)), 3600)
    m, _ = divmod(rem, 60)

    send_message(
        "📊 گزارش کامل معامله بسته‌شده\n\n"
        f"🟢 نماد: {symbol}\n"
        f"📈 جهت: Long (Buy)\n"
        f"⏱ زمان ورود: {_fmt_epoch(entry_time_ts)}\n"
        f"⏱ زمان خروج: {_fmt_epoch(exit_time_ts)}\n"
        f"⏳ مدت معامله: {h} ساعت و {m} دقیقه\n\n"
        f"💰 قیمت ورود: {entry_price}\n"
        f"💰 قیمت خروج: {exit_price}\n"
        f"📦 حجم: {qty}\n"
        f"⚙️ اهرم: {leverage}x\n\n"
        f"✅ علت بسته شدن: {reason} (بر اساس علامت سود/ضرر تخمین زده شده)\n\n"
        f"📌 دلیل ورود (سیگنال):\n"
        f"رسیدن قیمت به سطح رند {level} از پایین\n\n"
        f"💵 سود/ضرر خالص (تخمینی از اختلاف موجودی): {pnl:+.2f} USDT ({pnl_pct:+.2f}٪)\n"
        f"💼 موجودی قبل: {balance_before:.2f} USDT\n"
        f"💼 موجودی بعد: {balance_after:.2f} USDT\n\n"
        f"🔢 شناسه سفارش: {order_id}"
    )
