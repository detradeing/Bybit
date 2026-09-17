from pybit.unified_trading import HTTP
from src.config import (
    BYBIT_API_KEY, BYBIT_API_SECRET, SYMBOL, CATEGORY, LEVERAGE
)

# demo=True => حساب دمو بای‌بیت (پول واقعی درگیر نمی‌شه)
session = HTTP(
    demo=True,
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET,
)


def get_price():
    r = session.get_tickers(category=CATEGORY, symbol=SYMBOL)
    return float(r["result"]["list"][0]["lastPrice"])


def get_wallet_balance():
    r = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
    coin = r["result"]["list"][0]["coin"][0]
    return float(coin["walletBalance"])


def ensure_leverage():
    try:
        session.set_leverage(
            category=CATEGORY, symbol=SYMBOL,
            buyLeverage=str(LEVERAGE), sellLeverage=str(LEVERAGE),
        )
    except Exception:
        pass  # اگه از قبل همین مقدار تنظیم باشه، بای‌بیت خطا می‌ده؛ بی‌خطره


def ensure_isolated_margin():
    try:
        session.switch_margin_mode(
            category=CATEGORY, symbol=SYMBOL,
            tradeMode=1,  # 1 = isolated
            buyLeverage=str(LEVERAGE), sellLeverage=str(LEVERAGE),
        )
    except Exception:
        pass


def open_long(qty, entry_price, tp_price, sl_price):
    order = session.place_order(
        category=CATEGORY,
        symbol=SYMBOL,
        side="Buy",
        orderType="Market",
        qty=str(qty),
        takeProfit=str(round(tp_price, 1)),
        stopLoss=str(round(sl_price, 1)),
        tpTriggerBy="LastPrice",
        slTriggerBy="LastPrice",
    )
    return order["result"]


def get_open_position():
    r = session.get_positions(category=CATEGORY, symbol=SYMBOL)
    for pos in r["result"]["list"]:
        if float(pos.get("size", 0)) > 0:
            return pos
    return None


def get_last_exit_fill():
    """
    آخرین فیل (execution) بسته‌شدن معامله، برای استخراج قیمت خروج و شناسه سفارش.
    توجه: اندپوینت get_closed_pnl روی حساب دمو بای‌بیت پشتیبانی نمی‌شود (ErrCode 10032)،
    پس به‌جای آن از get_executions (که روی دمو کار می‌کند) استفاده می‌شود.
    """
    try:
        r = session.get_executions(category=CATEGORY, symbol=SYMBOL, limit=1)
        lst = r["result"]["list"]
        return lst[0] if lst else None
    except Exception:
        return None
