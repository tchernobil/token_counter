from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Budget:
    remaining: int
    normal_per_day: Optional[int]
    remaining_per_day: Optional[int]
    ratio_percent: Optional[float]
    overrun: bool
    to_save: Optional[int] = None


def compute_budget(
    total: int, used: int, month_working_days: int, remaining_days: int
) -> Budget:
    remaining = total - used
    normal = total // month_working_days if month_working_days > 0 else None
    per_day = remaining // remaining_days if remaining > 0 and remaining_days > 0 else None
    ratio = per_day / normal * 100 if per_day is not None and normal else None
    to_save = (
        max(0, normal * remaining_days - remaining)
        if normal is not None and remaining_days > 0
        else None
    )
    return Budget(
        remaining=remaining,
        normal_per_day=normal,
        remaining_per_day=per_day,
        ratio_percent=ratio,
        overrun=remaining < 0,
        to_save=to_save,
    )
