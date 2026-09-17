import os

BYBIT_API_KEY = os.environ["BYBIT_API_KEY"]
BYBIT_API_SECRET = os.environ["BYBIT_API_SECRET"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SYMBOL = "BTCUSDT"
CATEGORY = "linear"
LEVERAGE = 5
POSITION_PCT = 0.05          # 5% از موجودی دمو
TP_OFFSET = 700              # دلار
SL_OFFSET = 150              # دلار
LEVEL_TOLERANCE = 20         # دلار، بازه اطراف سطح رند
LEVEL_STEP_DIGITS = {0, 5, 8}  # رقم یکان هزارگان مجاز (60000, 65000, 68000, ...)
LOOKBACK_HOURS = 24

STATE_FILE = "state.json"
HISTORY_FILE = "price_history.json"
