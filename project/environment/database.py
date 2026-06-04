import sqlite3
import logging
from typing import List, Optional
from config import DB_PATH
from models import Station, AudioMetadata, Clue

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self._memory_conn = None

    def get_connection(self) -> sqlite3.Connection:
        if self.db_path == ":memory:":
            if self._memory_conn is None:
                self._memory_conn = sqlite3.connect(self.db_path)
                self._memory_conn.row_factory = sqlite3.Row
            return self._memory_conn
            
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_schema(self):
        schema = """
        CREATE TABLE IF NOT EXISTS stations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            frequency TEXT NOT NULL UNIQUE,
            audio_file TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS audio_metadata (
            id INTEGER PRIMARY KEY,
            station_id INTEGER NOT NULL,
            duration REAL NOT NULL,
            peak_volume REAL NOT NULL,
            sample_rate INTEGER NOT NULL,
            bitrate INTEGER,
            FOREIGN KEY (station_id) REFERENCES stations (id)
        );
        
        CREATE TABLE IF NOT EXISTS clues (
            id INTEGER PRIMARY KEY,
            station_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY (station_id) REFERENCES stations (id)
        );
        """
        try:
            with self.get_connection() as conn:
                conn.executescript(schema)
                logger.info("Database schema initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing schema: {e}")
            raise

    def insert_station(self, station: Station) -> int:
        query = "INSERT INTO stations (name, frequency, audio_file) VALUES (?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.execute(query, (station.name, station.frequency, station.audio_file))
            return cursor.lastrowid

    def insert_audio_metadata(self, metadata: AudioMetadata) -> int:
        query = """
        INSERT INTO audio_metadata (station_id, duration, peak_volume, sample_rate, bitrate) 
        VALUES (?, ?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, (
                metadata.station_id, metadata.duration, metadata.peak_volume, 
                metadata.sample_rate, metadata.bitrate
            ))
            return cursor.lastrowid

    def insert_clue(self, clue: Clue) -> int:
        query = "INSERT INTO clues (station_id, message) VALUES (?, ?)"
        with self.get_connection() as conn:
            cursor = conn.execute(query, (clue.station_id, clue.message))
            return cursor.lastrowid

    def get_all_stations(self) -> List[Station]:
        query = "SELECT * FROM stations"
        with self.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [Station(**dict(row)) for row in rows]

    def get_station_by_frequency(self, frequency: str) -> Optional[Station]:
        query = "SELECT * FROM stations WHERE frequency = ?"
        with self.get_connection() as conn:
            row = conn.execute(query, (frequency,)).fetchone()
            if row:
                return Station(**dict(row))
        return None

    def get_clue_for_station(self, station_id: int) -> Optional[Clue]:
        query = "SELECT * FROM clues WHERE station_id = ?"
        with self.get_connection() as conn:
            row = conn.execute(query, (station_id,)).fetchone()
            if row:
                return Clue(**dict(row))
        return None
