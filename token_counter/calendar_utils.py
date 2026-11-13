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


JOURS = ["Di", "Lu", "Ma", "Me", "Je", "Ve", "Sa"]

MOIS = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]


def render_month(today: date, holidays, strike: bool = False) -> str:
    """Calendrier texte en tableau : * aujourd'hui, & férié, . week-end.

    Avec strike, les jours ouvrés passés sont barrés (caractère combinant U+0336, sans séquence d'échappement).
    """
    width = 6
    border = "+" + "+".join("-" * width for _ in range(7)) + "+"
    title = f"{MOIS[today.month - 1]} {today.year}".center(len(border)).rstrip()
    lines = [
        "",
        title,
        border,
        "|" + "|".join(f"{n:^{width}}" for n in JOURS) + "|",
        border,
    ]
    for week in calendar.Calendar(firstweekday=6).monthdayscalendar(
        today.year, today.month
    ):
        cells = []
        for d in week:
            if d == 0:
                cells.append(" " * width)
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
            number = str(d)
            pad = " " * (3 - len(number))
            body = f" {number}{mark}"
            if strike and current < today and current.weekday() < 5:
                body = "".join(c + "\u0336" for c in body)
            cells.append(pad[:-1] + body + "  ")
        lines.append("|" + "|".join(cells) + "|")
        lines.append(border)
    lines.append("(* aujourd'hui, & férié, . week-end)")
    return "\n".join(lines)
