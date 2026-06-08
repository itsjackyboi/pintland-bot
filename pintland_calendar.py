from datetime import datetime, date
import json

with open("config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

EPOCH = datetime.strptime(cfg["epoch"], "%Y-%m-%d").date()

YEAR_DAYS = cfg["year_days"]        # 360
SEASON_DAYS = cfg["season_days"]    # 117
HOLIDAY_START = cfg["holiday_start"]

SEASONS = cfg["seasons"]
WEEK_DAYS = cfg["week_days"]
HOLIDAY_NAME = cfg["holiday_name"]

# Cycle anchor (Jan 1 2026 = Cycle 5)
CYCLE_OFFSET = 5


def get_pintland_date(today=None):
    if today is None:
        today = date.today()

    delta_days = (today - EPOCH).days

    cycle = (delta_days // YEAR_DAYS) + CYCLE_OFFSET
    day_of_year = delta_days % YEAR_DAYS

    week_day = WEEK_DAYS[day_of_year % len(WEEK_DAYS)]

    if day_of_year >= HOLIDAY_START:
        return {
            "cycle": cycle,
            "season": HOLIDAY_NAME,
            "season_day": (day_of_year - HOLIDAY_START) + 1,
            "week_day": week_day,
            "year_day": day_of_year + 1,
            "is_holiday": True
        }

    season_index = day_of_year // SEASON_DAYS
    season_day = (day_of_year % SEASON_DAYS) + 1

    return {
        "cycle": cycle,
        "season": SEASONS[season_index],
        "season_day": season_day,
        "week_day": week_day,
        "year_day": day_of_year + 1,
        "is_holiday": False
    }


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def format_message():
    p = get_pintland_date()

    keg_number = ((p["season_day"] - 1) // 9) + 1

    return (
        f"🍺 Good morning Liquor Kings.\n\n"
        f"Today is {p['week_day']} in the {ordinal(keg_number)} Keg of {p['season']}: Cycle {p['cycle']}.\n\n"
        f"Happy Drinking!"
    )