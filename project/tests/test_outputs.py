import pytest  # pyrefly: ignore [missing-import]
from pathlib import Path
import sqlite3

# pyrefly: ignore [missing-import]
from database import Database
# pyrefly: ignore [missing-import]
from models import Station, AudioMetadata, Clue
# pyrefly: ignore [missing-import]
from game_engine import GameEngine
# pyrefly: ignore [missing-import]
from config import FINAL_CODE
# pyrefly: ignore [missing-import]
from audio_processor import AudioProcessor
# pyrefly: ignore [missing-import]
from terminal_ui import TerminalUI

# --- Database Fixtures & Tests ---

@pytest.fixture
def db():
    db = Database(":memory:")
    db.initialize_schema()
    return db

def test_database_initialization(db):
    """Verifies that the database initializes correctly with all required tables and constraints."""
    conn = db.get_connection()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = [t['name'] for t in tables]
    assert 'stations' in table_names, "stations table is missing"
    assert 'audio_metadata' in table_names, "audio_metadata table is missing"
    assert 'clues' in table_names, "clues table is missing"
    
    # Check schema specifics
    station_info = conn.execute("PRAGMA table_info(stations)").fetchall()
    assert any(col['name'] == 'frequency' and col['notnull'] for col in station_info)

def test_insert_and_get_station(db):
    """Tests inserting a station and retrieving it by its frequency."""
    station = Station(id=None, name="Radio One", frequency="101.1", audio_file="station1.wav")
    sid = db.insert_station(station)
    assert sid > 0, "Insert should return valid ID"
    
    stations = db.get_all_stations()
    assert len(stations) == 1
    assert stations[0].name == "Radio One"
    assert stations[0].frequency == "101.1"

    fetched = db.get_station_by_frequency("101.1")
    assert fetched is not None
    assert fetched.id == sid

def test_station_frequency_unique(db):
    """Ensures that station frequencies must be unique in the database."""
    s1 = Station(id=None, name="Radio One", frequency="101.1", audio_file="station1.wav")
    db.insert_station(s1)
    s2 = Station(id=None, name="Radio Two", frequency="101.1", audio_file="station2.wav")
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_station(s2)

def test_insert_metadata(db):
    """Tests inserting and retrieving audio metadata for a station."""
    station = Station(id=None, name="S1", frequency="101.1", audio_file="station1.wav")
    sid = db.insert_station(station)
    
    metadata = AudioMetadata(id=None, station_id=sid, duration=1.5, peak_volume=-5.0, sample_rate=44100, bitrate=128000)
    mid = db.insert_audio_metadata(metadata)
    assert mid > 0
    
    conn = db.get_connection()
    row = conn.execute("SELECT * FROM audio_metadata WHERE id = ?", (mid,)).fetchone()
    assert row['duration'] == 1.5
    assert row['peak_volume'] == -5.0

def test_insert_and_get_clue(db):
    """Tests inserting and retrieving a clue associated with a station."""
    station = Station(id=None, name="S1", frequency="1.1", audio_file="1.wav")
    sid = db.insert_station(station)
    
    clue = Clue(id=None, station_id=sid, message="The first digit is 7.")
    cid = db.insert_clue(clue)
    assert cid > 0
    
    fetched = db.get_clue_for_station(sid)
    assert fetched is not None
    assert fetched.message == "The first digit is 7."

# --- Game Engine Fixtures & Tests ---

@pytest.fixture
def engine():
    db = Database(":memory:")
    db.initialize_schema()
    
    s1_id = db.insert_station(Station(id=None, name="S1", frequency="101.1", audio_file="station1.wav"))
    db.insert_clue(Clue(id=None, station_id=s1_id, message="Clue 1"))
    
    s2_id = db.insert_station(Station(id=None, name="S2", frequency="102.2", audio_file="station2.wav"))
    db.insert_clue(Clue(id=None, station_id=s2_id, message="Clue 2"))
    
    return GameEngine(db)

def test_scan_stations(engine):
    """Scanning stations returns available frequencies and logs the action."""
    freqs = engine.scan_stations()
    assert set(freqs) == {"101.1", "102.2"}
    assert "Player scanned for stations." in engine.get_logs()

def test_tune_valid_station(engine):
    """Tuning to a valid frequency connects and unlocks the clue."""
    msg = engine.tune("101.1")
    assert "Connected to S1" in msg
    clues = engine.get_clues()
    assert len(clues) == 1
    assert clues[0] == "Clue 1"
    
    # Tune again to same station shouldn't duplicate clue
    engine.tune("101.1")
    assert len(engine.get_clues()) == 1

def test_tune_invalid_station(engine):
    """Tuning to a non-existent frequency returns static noise."""
    msg = engine.tune("99.9")
    assert "Static noise... No station found at this frequency." in msg
    assert len(engine.get_clues()) == 0

def test_clue_progression(engine):
    """Tuning to multiple stations correctly accumulates clues."""
    engine.tune("101.1")
    assert len(engine.get_clues()) == 1
    engine.tune("102.2")
    assert len(engine.get_clues()) == 2
    assert "Clue 1" in engine.get_clues()
    assert "Clue 2" in engine.get_clues()

@pytest.mark.parametrize("code,expected", [
    (FINAL_CODE, True),
    ("0000", False),
    ("9999", False)
])
def test_submit_code(engine, code, expected):
    """Submitting the correct final code returns True, otherwise False."""
    assert engine.submit_code(code) is expected
    assert any(f"submitted escape code: {code}" in log for log in engine.get_logs())

def test_logs_tracked(engine):
    """Game engine correctly logs significant actions like scanning, tuning, finding clues, and submitting codes."""
    engine.scan_stations()
    engine.tune("101.1")
    engine.submit_code("1234")
    
    logs = engine.get_logs()
    assert "Player scanned for stations." in logs[0]
    assert "Player tuned to S1 (101.1)." in logs[1]
    assert "Player discovered a clue on S1." in logs[2]
    assert "Player submitted escape code: 1234" in logs[3]


# --- Audio Processor Fixtures & Tests ---

@pytest.fixture
def audio_dir():
    # Use real project audio dir which contains station1.wav etc
    return Path("/app/audio")

def test_extract_metadata_real_file(db, audio_dir):
    """AudioProcessor successfully extracts metadata like duration, sample rate, and bitrate from a real file."""
    processor = AudioProcessor(db, audio_dir)
    result = processor.extract_metadata("station1.wav")
    assert result is not None
    assert result['sample_rate'] == 44100
    assert result['duration'] == 1.0
    assert result['bitrate'] == 706224

def test_extract_metadata_station2(db, audio_dir):
    """AudioProcessor successfully extracts metadata from station2.wav."""
    processor = AudioProcessor(db, audio_dir)
    result = processor.extract_metadata("station2.wav")
    assert result is not None
    assert result['sample_rate'] == 44100
    assert result['duration'] == 1.0
    assert result['bitrate'] == 706224

def test_extract_metadata_station3(db, audio_dir):
    """AudioProcessor successfully extracts metadata from station3.wav."""
    processor = AudioProcessor(db, audio_dir)
    result = processor.extract_metadata("station3.wav")
    assert result is not None
    assert result['sample_rate'] == 44100
    assert result['duration'] == 1.0
    assert result['bitrate'] == 706224


def test_extract_peak_volume_real_file(db, audio_dir):
    """AudioProcessor successfully extracts peak volume from a real file."""
    processor = AudioProcessor(db, audio_dir)
    result = processor.extract_peak_volume("station1.wav")
    assert result is not None
    assert isinstance(result, float)
    assert abs(result - (-18.1)) < 0.2

def test_extract_metadata_missing_file(db, audio_dir):
    """AudioProcessor gracefully handles extracting metadata from a missing file."""
    processor = AudioProcessor(db, audio_dir)
    result = processor.extract_metadata("missing.wav")
    assert result is None

def test_process_all_stations(db, audio_dir):
    """AudioProcessor correctly processes all valid station files in the database and updates metadata."""
    db.insert_station(Station(id=None, name="Station 1", frequency="101.1", audio_file="station1.wav"))
    db.insert_station(Station(id=None, name="Missing", frequency="99.9", audio_file="missing.wav"))
    
    processor = AudioProcessor(db, audio_dir)
    processor.process_all_stations()
    
    conn = db.get_connection()
    count = conn.execute("SELECT COUNT(*) FROM audio_metadata").fetchone()[0]
    assert count == 1, "Should only process existing files"
    
    meta = conn.execute("SELECT * FROM audio_metadata").fetchone()
    assert meta['sample_rate'] == 44100
    assert meta['duration'] == 1.0
    assert meta['bitrate'] == 706224
    assert abs(meta['peak_volume'] - (-18.1)) < 0.2


# --- Terminal UI Fixtures & Tests ---

@pytest.fixture
def terminal_engine():
    db = Database(":memory:")
    db.initialize_schema()
    s1_id = db.insert_station(Station(id=None, name="S1", frequency="101.1", audio_file="station1.wav"))
    db.insert_clue(Clue(id=None, station_id=s1_id, message="Clue 1"))
    return GameEngine(db)

def test_cmd_help(terminal_engine, capsys):
    """The help command displays a list of available commands including scan and tune."""
    ui = TerminalUI(terminal_engine)
    ui.cmd_help()
    out, _ = capsys.readouterr()
    assert "Available commands" in out
    assert "scan" in out
    assert "tune" in out

def test_cmd_scan(terminal_engine, capsys):
    """The scan command outputs available frequencies."""
    ui = TerminalUI(terminal_engine)
    ui.cmd_scan()
    out, _ = capsys.readouterr()
    assert "Available Stations:" in out
    assert "101.1 FM" in out

def test_cmd_tune(terminal_engine, capsys):
    """The tune command connects to a specified frequency and updates the current station."""
    ui = TerminalUI(terminal_engine)
    ui.cmd_tune("101.1")
    out, _ = capsys.readouterr()
    assert "Connected to S1" in out
    assert terminal_engine.current_station is not None
    assert terminal_engine.current_station.frequency == "101.1"

def test_cmd_logs_and_clues(terminal_engine, capsys):
    """The logs and clues commands correctly display the user's action history and collected clues."""
    ui = TerminalUI(terminal_engine)
    ui.cmd_tune("101.1")
    capsys.readouterr() # clear
    
    ui.cmd_logs()
    out, _ = capsys.readouterr()
    assert "Player tuned to S1" in out
    
    ui.cmd_clues()
    out, _ = capsys.readouterr()
    assert "Clue 1" in out

def test_cmd_status(terminal_engine, capsys):
    """The status command accurately reflects whether the radio is off or tuned to a specific station."""
    ui = TerminalUI(terminal_engine)
    ui.cmd_status()
    out, _ = capsys.readouterr()
    assert "Radio is off" in out
    
    ui.cmd_tune("101.1")
    capsys.readouterr() # clear
    
    ui.cmd_status()
    out, _ = capsys.readouterr()
    assert "Currently tuned to: S1" in out

def test_cmd_submit(terminal_engine, capsys):
    """The submit command correctly evaluates the submitted code and outputs success or failure."""
    ui = TerminalUI(terminal_engine)
    res = ui.cmd_submit(FINAL_CODE)
    out, _ = capsys.readouterr()
    assert res is True
    assert "You Escaped!" in out
    
    res2 = ui.cmd_submit("WRONG")
    out2, _ = capsys.readouterr()
    assert res2 is False
    assert "Access Denied" in out2

def test_end_to_end_gameplay(terminal_engine, monkeypatch, capsys):
    """Simulates a full gameplay sequence from scanning to successfully submitting the final code."""
    ui = TerminalUI(terminal_engine)
    
    # Simulate user inputs
    inputs = ["scan", "tune 101.1", "clues", f"submit {FINAL_CODE}"]
    input_gen = (i for i in inputs)
    monkeypatch.setattr('builtins.input', lambda _: next(input_gen))
    
    # The loop should break when submit is successful
    ui.start()
    out, _ = capsys.readouterr()
    
    assert "Available Stations:" in out
    assert "Connected to S1" in out
    assert "Clue 1" in out
    assert "You Escaped!" in out

def test_integration_full_gameplay():
    """Integration test verifying station scanning, tuning, and basic code submission functionality."""
    db = Database(":memory:")
    db.initialize_schema()
    s1_id = db.insert_station(Station(id=None, name="Radio One", frequency="101.1", audio_file="station1.wav"))
    db.insert_station(Station(id=None, name="Radio Two", frequency="102.2", audio_file="station2.wav"))
    db.insert_station(Station(id=None, name="Radio Three", frequency="103.3", audio_file="station3.wav"))
    db.insert_clue(Clue(id=None, station_id=s1_id, message="Clue 1"))
    
    engine = GameEngine(db)
    freqs = engine.scan_stations()
    assert len(freqs) == 3
    for f in freqs:
        msg = engine.tune(f)
        assert "Connected" in msg or "Static noise" in msg
    
    assert engine.submit_code(FINAL_CODE) is True
