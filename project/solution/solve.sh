#!/bin/bash
set -e

# Overwrite files with correct implementation
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "/app" ]; then
    TARGET_DIR="/app"
else
    TARGET_DIR="$(cd "$SCRIPT_DIR/../environment" && pwd)"
fi

cat << 'EOF' > "$TARGET_DIR/database.py"
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
EOF

cat << 'EOF' > "$TARGET_DIR/game_engine.py"
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
EOF

cat << 'EOF' > "$TARGET_DIR/audio_processor.py"
import json
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from config import AUDIO_DIR
from models import AudioMetadata
from database import Database

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, db: Database, audio_dir: Path = AUDIO_DIR):
        self.db = db
        self.audio_dir = audio_dir

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        full_path = self.audio_dir / file_path
        if not full_path.exists():
            logger.warning(f"Audio file not found: {full_path}")
            return None

        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', str(full_path)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            stream = next((s for s in data.get('streams', []) if s['codec_type'] == 'audio'), None)
            if not stream:
                return None
                
            format_data = data.get('format', {})
            return {
                'duration': float(format_data.get('duration', 0)),
                'sample_rate': int(stream.get('sample_rate', 0)),
                'bitrate': int(format_data.get('bit_rate', 0)) if format_data.get('bit_rate') else None
            }
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.error(f"Failed to extract metadata for {file_path}: {e}")
            return None

    def extract_peak_volume(self, file_path: str) -> Optional[float]:
        full_path = self.audio_dir / file_path
        if not full_path.exists():
            return None

        cmd = [
            'ffmpeg', '-i', str(full_path), '-af', 'volumedetect',
            '-vn', '-sn', '-dn', '-f', 'null', '/dev/null'
        ]
        
        if subprocess.os.name == 'nt':
            cmd[-1] = 'NUL'
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            for line in result.stderr.split('\n'):
                if 'max_volume:' in line:
                    vol_str = line.split('max_volume:')[1].strip().replace(' dB', '')
                    return float(vol_str)
            return 0.0
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract peak volume for {file_path}: {e}")
            return None

    def process_all_stations(self):
        stations = self.db.get_all_stations()
        for station in stations:
            logger.info(f"Processing audio for {station.name} ({station.audio_file})")
            
            base_meta = self.extract_metadata(station.audio_file)
            peak_vol = self.extract_peak_volume(station.audio_file)
            
            if base_meta is not None and peak_vol is not None:
                metadata = AudioMetadata(
                    id=None,
                    station_id=station.id,
                    duration=base_meta['duration'],
                    peak_volume=peak_vol,
                    sample_rate=base_meta['sample_rate'],
                    bitrate=base_meta['bitrate']
                )
                self.db.insert_audio_metadata(metadata)
                logger.info(f"Successfully processed {station.name}.")
            else:
                logger.warning(f"Could not fully process audio for {station.name}.")
EOF

cat << 'EOF' > "$TARGET_DIR/terminal_ui.py"
import sys
from game_engine import GameEngine

class TerminalUI:
    def __init__(self, engine: GameEngine):
        self.engine = engine

    def start(self):
        print("Welcome to the SQLite-Backed FFmpeg Terminal Radio Escape Puzzle")
        print("Type 'help' for a list of commands.")
        
        while True:
            try:
                command_input = input("\n> ").strip().split(" ", 1)
                if not command_input or not command_input[0]:
                    continue
                
                command = command_input[0].lower()
                args = command_input[1] if len(command_input) > 1 else ""
                
                if command == "exit":
                    print("Exiting game...")
                    sys.exit(0)
                elif command == "help":
                    self.cmd_help()
                elif command == "scan":
                    self.cmd_scan()
                elif command == "stations":
                    self.cmd_scan()
                elif command == "tune":
                    self.cmd_tune(args)
                elif command == "logs":
                    self.cmd_logs()
                elif command == "clues":
                    self.cmd_clues()
                elif command == "status":
                    self.cmd_status()
                elif command == "submit":
                    if self.cmd_submit(args):
                        break
                else:
                    print("Unknown command. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\nExiting game...")
                sys.exit(0)
            except Exception as e:
                print(f"An error occurred: {e}")

    def cmd_help(self):
        print("Available commands:")
        print("  help             - Show this help message")
        print("  scan/stations    - Scan for available station frequencies")
        print("  tune <frequency> - Tune the radio to a specific frequency")
        print("  logs             - View activity logs")
        print("  clues            - Review unlocked clues")
        print("  status           - See current radio status")
        print("  submit <code>    - Submit the final escape code")
        print("  exit             - Exit the game")

    def cmd_scan(self):
        frequencies = self.engine.scan_stations()
        print("Available Stations:")
        for freq in frequencies:
            print(f"{freq} FM")

    def cmd_tune(self, args: str):
        if not args:
            print("Please specify a frequency. Example: tune 101.1")
            return
        
        freq = args.replace(" FM", "").replace(" fm", "").strip()
        result = self.engine.tune(freq)
        print(result)

    def cmd_logs(self):
        logs = self.engine.get_logs()
        if not logs:
            print("No logs available yet.")
            return
            
        print("Showing station logs...")
        for log in logs:
            print(f"- {log}")

    def cmd_clues(self):
        clues = self.engine.get_clues()
        if not clues:
            print("No clues discovered yet. Try tuning to different stations.")
            return
            
        print("Discovered Clues:")
        for clue in clues:
            print(f'"{clue}"')

    def cmd_status(self):
        if self.engine.current_station:
            print(f"Currently tuned to: {self.engine.current_station.name} ({self.engine.current_station.frequency} FM)")
        else:
            print("Radio is off. Use 'tune' to connect to a station.")

    def cmd_submit(self, args: str) -> bool:
        if not args:
            print("Please provide a code. Example: submit 1234")
            return False
            
        if self.engine.submit_code(args):
            print("You Escaped!")
            return True
        else:
            print("Access Denied")
            return False
EOF

exit 0
