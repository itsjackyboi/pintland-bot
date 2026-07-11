from datetime import datetime, date
from zoneinfo import ZoneInfo
import re

# -----------------------------
# PINTLAND CONFIG
# -----------------------------
DAY_NAMES = [
    "Mooringday", "Brewsday", "Tidecall",
    "Grogsnap", "Beastwatch", "Lagerhorn",
    "Bloodwake", "Keeldrift", "Hangover"
]

EPOCH = date(2026, 1, 1)
BASE_YEAR = 466
BASE_CYCLE = 93

# -----------------------------
# PINTLAND HOLIDAYS
# Loaded from holidays.json — add new holidays there, not here.
# Fields:
#   name         : Display name
#   doy_start    : First day of holiday (Pintland day-of-year, 1-360)
#   doy_end      : Last day of holiday (same as doy_start for single-day)
#   description  : Shown on the first day of the holiday
#   notes        : (optional) Human-readable reminder of what the date maps to
#   one_time_year: (optional) If set, holiday only fires in that Pintland year
# -----------------------------
def load_holidays():
    import tomllib
    with open("holidays.toml", "rb") as f:
        data = tomllib.load(f)
    return data["holiday"]

HOLIDAYS = load_holidays()

# -----------------------------
# TIME (EST/EDT SAFE, NO PYTZ)
# -----------------------------
def get_today():
    eastern = ZoneInfo("America/New_York")
    return datetime.now(eastern).date()

# -----------------------------
# RUMORS
# -----------------------------
def load_rumors():
    with open("rumors.txt", "r", encoding="utf-8") as f:
        content = f.read()
    raw = re.split(r"\n(?=\d+\.\s)", content.strip())
    cleaned = []
    for r in raw:
        r = re.sub(r"^\d+\.\s*", "", r).strip()
        if r:
            cleaned.append(r)
    return cleaned

RUMORS = load_rumors()

# -----------------------------
# CORE LOGIC
# -----------------------------
def get_calendar_data():
    today = get_today()
    delta_days = (today - EPOCH).days

    dik = delta_days % 9
    day_name = DAY_NAMES[dik]

    doy = (delta_days % 360) + 1

    if doy <= 117:
        season = "Stormtide"
        keg = (doy - 1) // 9 + 1
    elif doy <= 234:
        season = "Goldsun"
        keg = (doy - 118) // 9 + 1
    elif doy <= 351:
        season = "Veilfrost"
        keg = (doy - 235) // 9 + 1
    else:
        season = "Holiday"
        keg = 1

    year_offset = delta_days // 360
    pint_year = BASE_YEAR + year_offset
    cycle = BASE_CYCLE + (year_offset // 5)

    return {
        "day_name": day_name,
        "season": season,
        "keg": keg,
        "year": pint_year,
        "cycle": cycle,
        "doy": doy
    }

# -----------------------------
# RUMOR PICK
# -----------------------------
def get_rumor(doy):
    if not RUMORS:
        return None
    return RUMORS[(doy - 1) % len(RUMORS)]

# -----------------------------
# HOLIDAY CHECK
# Compares today's doy against each holiday's doy range.
# Countdown looks ahead up to 3 days, wrapping across the year boundary.
# -----------------------------
def get_holiday_notice(doy, pint_year):
    notices = []
    seen_upcoming = set()

    for holiday in HOLIDAYS:
        start = holiday["doy_start"]
        end   = holiday["doy_end"]

        # Skip one-time holidays that don't match the current Pintland year
        if "one_time_year" in holiday and holiday["one_time_year"] != pint_year:
            continue

        # Is today inside the holiday range?
        if start <= doy <= end:
            # Only show description on the first day of a multi-day holiday
            show_desc = (doy == start)
            notices.append({
                "type": "today",
                "name": holiday["name"],
                "description": holiday["description"] if show_desc else None,
            })

        # Is the start of this holiday 1–3 days away?
        else:
            for lookahead in range(1, 4):
                future_doy = (doy - 1 + lookahead) % 360 + 1  # wraps year boundary
                if future_doy == start:
                    key = holiday["name"]
                    if key not in seen_upcoming:
                        seen_upcoming.add(key)
                        notices.append({
                            "type": "upcoming",
                            "name": holiday["name"],
                            "days": lookahead,
                        })
                    break

    return notices

# -----------------------------
# FINAL MESSAGE
# -----------------------------
def format_message():
    p = get_calendar_data()
    rumor = get_rumor(p["doy"])
    notices = get_holiday_notice(p["doy"], p["year"])

    msg = f"""🍺 Good morning Liquor Kings.

Today is {p['day_name']} in the {p['keg']}th Keg of {p['season']}.
Year {p['year']} — Cycle {p['cycle']}."""

    if notices:
        msg += "\n"
        for notice in notices:
            if notice["type"] == "today":
                if notice["description"]:
                    msg += f"\n🎉 **Today is {notice['name']}!**\n{notice['description']}"
                else:
                    msg += f"\n🎉 **Today is {notice['name']}!**"
            elif notice["type"] == "upcoming":
                days = notice["days"]
                day_word = "day" if days == 1 else "days"
                msg += f"\n📅 {days} {day_word} until **{notice['name']}**!"

    msg += f"""

📜 Tavern Rumor
{rumor if rumor else "No rumor today..."}

Happy Drinking!"""

    return msg
