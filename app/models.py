from pymongo import MongoClient
from dataclasses import dataclass, field
from typing import Optional
from bson import ObjectId
from datetime import datetime

@dataclass
class GeoPoint:
    id: Optional[ObjectId] = field(default=None)
    latitude: float = 0.0
    longitude: float = 0.0
    address: str = ""
    event_id: Optional[ObjectId] = field(default=None)

@dataclass
class Event:
    id: Optional[ObjectId] = field(default=None)
    image_url: str = ""
    host: str = ""
    title: str = ""
    date: str = ""
    location: str = ""
    description: str = ""
    tags: str = ""
    extra_info: str = ""
    bio: str = ""
    exact_address: bool = False
    accepts_refunds: bool = False

@dataclass
class EventInfo:
    id: Optional[ObjectId] = field(default=None)
    event_id: Optional[ObjectId] = field(default=None)
    max_capacity: int = 0
    current_capacity: int = 0
    host_name: str = ""
    vip_eligible: bool = False
    tags: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
