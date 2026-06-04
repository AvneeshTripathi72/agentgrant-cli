from dataclasses import dataclass
from typing import Optional

@dataclass
class Station:
    id: Optional[int]
    name: str
    frequency: str
    audio_file: str

@dataclass
class AudioMetadata:
    id: Optional[int]
    station_id: int
    duration: float
    peak_volume: float
    sample_rate: int
    bitrate: Optional[int] = None

@dataclass
class Clue:
    id: Optional[int]
    station_id: int
    message: str
