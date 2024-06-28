from dataclasses import dataclass


@dataclass
class DataArray:
    time: float
    depth: list
    temp: list
    place: str
