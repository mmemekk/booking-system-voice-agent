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
    party_size: Optional[int] = None
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
            "party_size": self.party_size or "unknown",
            "special_request": self.special_request or "none",
        }

        return yaml.dump(data)
    
    def check_availability_request(self) -> Optional[dict]:
        
        if self.reservation_date is None or self.reservation_time is None or self.party_size is None:
            return None
        
        DATE_FORMAT = "%Y-%m-%d"
        TIME_FORMAT = "%H:%M"   

        return {
            "date": self.reservation_date.strftime(DATE_FORMAT),
            "time": self.reservation_time.strftime(TIME_FORMAT),
            "capacity": self.party_size,
            "maxAlternative": 4
        }
        
    def create_reservation_request(self) -> Optional[dict]:
        
        if self.reservation_date is None or self.reservation_time is None or self.party_size is None or self.customer_name is None or self.customer_phone is None:
            return None
        
        DATE_FORMAT = "%Y-%m-%d"
        TIME_FORMAT = "%H:%M"   

        return {
            "customerName": self.customer_name,
            "customerPhone": self.customer_phone,
            "bookingDate": self.reservation_date.strftime(DATE_FORMAT),
            "bookingTime": self.reservation_time.strftime(TIME_FORMAT),
            "capacity": self.party_size,
        }        