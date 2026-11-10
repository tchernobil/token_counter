import calendar
from datetime import date


def is_working_day(day: date, holidays) -> bool:
    return day.weekday() < 5 and day not in holidays


def _month_days(year: int, month: int):
    last = calendar.monthrange(year, month)[1]
    return [date(year, month, d) for d in range(1, last + 1)]


def working_days_in_month(year: int, month: int, holidays) -> int:
    return sum(is_working_day(d, holidays) for d in _month_days(year, month))


def remaining_working_days(today: date, holidays) -> int:
    return sum(
        is_working_day(d, holidays)
        for d in _month_days(today.year, today.month)
        if d >= today
    )


MOIS = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]


def render_month(today: date, holidays) -> str:
    """Calendrier texte : * aujourd'hui, & férié, . week-end."""
    lines = [
        f"{MOIS[today.month - 1]} {today.year}".center(27).rstrip(),
        " Di  Lu  Ma  Me  Je  Ve  Sa",
    ]
    for week in calendar.Calendar(firstweekday=6).monthdayscalendar(
        today.year, today.month
    ):
        cells = []
        for d in week:
            if d == 0:
                cells.append("    ")
                continue
            current = date(today.year, today.month, d)
            if current == today:
                mark = "*"
            elif current in holidays:
                mark = "&"
            elif current.weekday() >= 5:
                mark = "."
            else:
                mark = " "
            cells.append(f"{d:>2}{mark} ")
        lines.append("".join(cells).rstrip())
    lines.append("(* aujourd'hui, & férié, . week-end)")
    return "\n".join(lines)
