from datetime import date
import json

with open("config.json", "r", encoding="utf-8") as f:
cfg = json.load(f)

# =====================================

# PINTLAND CALENDAR SETTINGS

# =====================================

# Jan 1, 2026 =

# Mooringday

# 1st Keg of Stormtide

# Year 466

# Cycle 93

EPOCH = date(2026, 1, 1)

START_YEAR = 466
START_CYCLE = 93

YEAR_DAYS = 360
SEASON_DAYS = 117
HOLIDAY_START = 351

SEASONS = cfg["seasons"]
WEEK_DAYS = cfg["week_days"]
HOLIDAY_NAME = cfg["holiday_name"]

# =====================================

# DATE CALCULATION

# =====================================

def get_pintland_date(today=None):
if today is None:
today = date.today()

```
delta_days = (today - EPOCH).days

years_passed = delta_days // YEAR_DAYS
year = START_YEAR + years_passed

cycle = START_CYCLE + ((year - START_YEAR) // 5)

day_of_year = delta_days % YEAR_DAYS

week_day = WEEK_DAYS[day_of_year % len(WEEK_DAYS)]

if day_of_year >= HOLIDAY_START:
    return {
        "cycle": cycle,
        "year": year,
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
    "year": year,
    "season": SEASONS[season_index],
    "season_day": season_day,
    "week_day": week_day,
    "year_day": day_of_year + 1,
    "is_holiday": False
}
```

# =====================================

# ORDINAL HELPER

# =====================================

def ordinal(n):
if 10 <= n % 100 <= 20:
suffix = "th"
else:
suffix = {
1: "st",
2: "nd",
3: "rd"
}.get(n % 10, "th")

```
return f"{n}{suffix}"
```

# =====================================

# DISCORD MESSAGE FORMAT

# =====================================

def format_message():
p = get_pintland_date()

```
keg_number = ((p["season_day"] - 1) // 9) + 1

# Load rumors
import re

with open("rumors.txt", "r", encoding="utf-8") as f:
    content = f.read()

matches = list(re.finditer(r"^\d+\.\s", content, re.MULTILINE))

rumors = []

for i in range(len(matches)):
    start = matches[i].start()

    if i + 1 < len(matches):
        end = matches[i + 1].start()
    else:
        end = len(content)

    rumors.append(content[start:end].strip())

rumor_index = p["year_day"] - 1

if rumor_index >= len(rumors):
    rumor_index = rumor_index % len(rumors)

rumor = rumors[rumor_index]

return (
    f"🍺 Good morning Liquor Kings.\n\n"
    f"Today is {p['week_day']} in the {ordinal(keg_number)} Keg of {p['season']}.\n\n"
    f"Year {p['year']} — Cycle {p['cycle']}.\n\n"
    f"📜 Tavern Rumor\n"
    f"{rumor}\n\n"
    f"Happy Drinking!"
)
```
