from src.config import LEVEL_TOLERANCE, LEVEL_STEP_DIGITS


def candidate_levels(price, tolerance=LEVEL_TOLERANCE):
    """سطوح رند هزارگان مجاز (یکان هزار در LEVEL_STEP_DIGITS) نزدیک قیمت فعلی."""
    levels = []
    base_k = int(price // 1000)
    for k in range(base_k - 2, base_k + 3):
        if k % 10 in LEVEL_STEP_DIGITS:
            level = k * 1000
            if abs(price - level) <= tolerance:
                levels.append(level)
    return levels


def check_entry_signal(price, prev_price, max_price_24h, tolerance=LEVEL_TOLERANCE):
    """
    برمی‌گردونه: سطح هدف اگر شرایط ورود Long برقرار باشه، وگرنه None.
    شرایط:
      1) قیمت فعلی داخل بازه یک سطح رند مجاز باشه.
      2) قیمت از پایین به سمت سطح اومده باشه (prev_price زیر بازه‌ی پایینی سطح بوده).
      3) در بازه لوک‌بک (۲۴س) قیمت هنوز به این سطح یا بالاتر نرسیده باشه.
    """
    if prev_price is None:
        return None

    for level in candidate_levels(price, tolerance):
        came_from_below = prev_price < (level - tolerance)
        already_touched = max_price_24h is not None and max_price_24h >= (level - tolerance)
        if came_from_below and not already_touched:
            return level
    return None
