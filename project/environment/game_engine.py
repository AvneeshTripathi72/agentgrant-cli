import logging
from typing import List, Optional
from database import Database
from models import Station, Clue
from config import FINAL_CODE

logger = logging.getLogger(__name__)

class GameEngine:
    def __init__(self, db: Database):
        self.db = db
        self.current_station: Optional[Station] = None
        self.unlocked_clues: List[Clue] = []
        self.logs: List[str] = []

    def scan_stations(self) -> List[str]:
        stations = self.db.get_all_stations()
        self.logs.append("Player scanned for stations.")
        return [s.frequency for s in stations]

    def tune(self, frequency: str) -> str:
        station = self.db.get_station_by_frequency(frequency)
        if station:
            self.current_station = station
            self.logs.append(f"Player tuned to {station.name} ({frequency}).")
            
            clue = self.db.get_clue_for_station(station.id)
            if clue:
                if not any(c.id == clue.id for c in self.unlocked_clues):
                    self.unlocked_clues.append(clue)
                    self.logs.append(f"Player discovered a clue on {station.name}.")
                    
            return f"Connected to {station.name}"
        else:
            self.logs.append(f"Player tried to tune to invalid frequency {frequency}.")
            return "Static noise... No station found at this frequency."

    def get_logs(self) -> List[str]:
        return self.logs

    def get_clues(self) -> List[str]:
        return [c.message for c in self.unlocked_clues]

    def submit_code(self, code: str) -> bool:
        self.logs.append(f"Player submitted escape code: {code}")
        return code == FINAL_CODE
