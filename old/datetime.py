from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class DateTimeInterval:
    start: Optional[datetime]
    end: Optional[datetime]


    @property
    def empty(self):
        return self.start is None or self.end is None

    def includes(self, dt: datetime) -> bool:
        if self.start is None:
            included_after = True
        else:
            included_after = self.start <= dt

        if self.end is None:
            included_before = True
        else:
            included_before = dt <= self.end

        return included_before and included_after

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end
