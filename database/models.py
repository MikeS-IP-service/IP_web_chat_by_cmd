from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Booking:
    id: Optional[int] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    service_type: Optional[str] = None
    booking_date: Optional[str] = None
    booking_time: Optional[str] = None
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    created_at: Optional[str] = None
    
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}