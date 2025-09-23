from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from bson import ObjectId

@dataclass
class Event:
    id: Optional[ObjectId] = None
    title: str = ""
    date: str = ""
    location: str = ""
    url: str = ""
    scraped_at: datetime = datetime.utcnow()
