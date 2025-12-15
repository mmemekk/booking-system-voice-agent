import yaml
from dataclasses import dataclass
from typing import Optional
from datetime import date, time

@dataclass
class UserData:

    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    reservation_date: Optional[date] = None
    reservation_time: Optional[time] = None
    reservation_capacity: Optional[int] = None
    special_request: Optional[str] = None

    def summarize(self) -> str:
        DATE_FORMAT = "%Y-%m-%d"
        TIME_FORMAT = "%H:%M"   
        data = {
            "customer_name": self.customer_name or "unknown",
            "customer_phone": self.customer_phone or "unknown",
            # "reservation_date": self.reservation_date or "unknown",
            # "reservation_time": self.reservation_time or "unknown",
            "reservation_date": self.reservation_date.strftime(DATE_FORMAT) if self.reservation_date is not None else "unknown",
            "reservation_time": self.reservation_time.strftime(TIME_FORMAT) if self.reservation_time is not None else "unknown",
            "reservation_capacity": self.reservation_capacity or "unknown",
            "special_request": self.special_request or "none",
        }

        return yaml.dump(data)