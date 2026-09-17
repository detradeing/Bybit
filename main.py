import time
from src import bybit_client as bb
from src import state as st
from src import telegram as tg
from src.strategy import check_entry_signal
from src.config import LEVERAGE, POSITION_PCT, TP_OFFSET, SL_OFFSET


def handle_no_open_position(price, history):
    prev_price = st.last_price_before_current(history)
    max_24h = st.max_price_in_window(history)
    level = check_entry_signal(price, prev_price, max_24h)
    if level is None:
        print(f"[INFO] بدون سیگنال. قیمت={price}")
        return

    bb.ensure_isolated_margin()
    bb.ensure_leverage()

    balance = bb.get_wallet_balance()
    margin = balance * POSITION_PCT
    notional = margin * LEVERAGE
    qty = round(notional / price, 3)  # دقت مقدار BTC؛ در صورت نیاز طبق instrument-info تنظیم شود

    tp_price = price + TP_OFFSET
    sl_price = price - SL_OFFSET

    bb.open_long(qty, price, tp_price, sl_price)

    state = st.load_state()
    state["open_position"] = {
        "entry_price": price,
        "level": level,
        "qty": qty,
        "balance_before": balance,
        "entry_time": time.time(),
    }
    st.save_state(state)

    tg.notify_open("BTCUSDT", price, qty, LEVERAGE, tp_price, sl_price, level)
    print(f"[INFO] پوزیشن Long باز شد. قیمت={price} سطح={level}")


def handle_check_close(open_pos):
    live_pos = bb.get_open_position()
    if live_pos is not None:
        print("[INFO] پوزیشن هنوز باز است.")
        return

    # پوزیشن روی صرافی بسته شده. get_closed_pnl روی حساب دمو پشتیبانی نمی‌شود،
    # پس قیمت خروج از آخرین fill و سود/ضرر از اختلاف موجودی محاسبه می‌شود.
    fill = bb.get_last_exit_fill()
    balance_after = bb.get_wallet_balance()
    exit_price = float(fill["execPrice"]) if fill else None
    order_id = fill["orderId"] if fill else "نامشخص"
    exit_time_ts = int(fill["execTime"]) / 1000 if fill else time.time()

    if exit_price is None:
        print("[WARN] پوزیشن بسته شده ولی fill خروج پیدا نشد؛ گزارش با اطلاعات ناقص ارسال می‌شود.")
        exit_price = "نامشخص"

    tg.notify_closed(
        symbol="BTCUSDT",
        entry_price=open_pos["entry_price"],
        exit_price=exit_price,
        qty=open_pos["qty"],
        leverage=LEVERAGE,
        entry_time_ts=open_pos.get("entry_time", exit_time_ts),
        exit_time_ts=exit_time_ts,
        order_id=order_id,
        balance_before=open_pos["balance_before"],
        balance_after=balance_after,
        level=open_pos["level"],
    )

    state = st.load_state()
    state["open_position"] = None
    st.save_state(state)
    print("[INFO] گزارش بسته‌شدن معامله ارسال شد.")


def main():
    price = bb.get_price()
    history = st.append_price(price)

    state = st.load_state()
    open_pos = state.get("open_position")

    if open_pos is None:
        handle_no_open_position(price, history)
    else:
        handle_check_close(open_pos)


if __name__ == "__main__":
    main()
