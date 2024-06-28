from dataclasses import dataclass


@dataclass
class Well:
    id: int
    name: str
    latitude: float
    longitude: float
    interval_start: float
    interval_end: float
    interval_value: float
    status: str
