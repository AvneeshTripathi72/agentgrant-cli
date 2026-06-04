# SQLite-Backed FFmpeg Terminal Radio Escape Puzzle

A terminal-based escape room game where players investigate fictional radio stations, inspect logs, analyze audio, discover clues, and submit a final escape code.

## Requirements
- Python 3.11+
- SQLite3
- FFmpeg and ffprobe in PATH

## Installation

1. Ensure FFmpeg is installed and accessible via command line.
2. Clone or download this project.
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Database Schema
The database uses the following tables:
- `stations`: Basic station information (name, frequency, audio file).
- `audio_metadata`: Properties extracted via FFmpeg (duration, peak_volume, sample_rate, bitrate).
- `clues`: Hidden messages tied to stations.

## Running the Game

To launch the game:
```bash
python main.py
```

## Gameplay Instructions
- Type `help` for available commands.
- Use `scan` to list available frequencies.
- `tune <frequency>` to connect to a station and listen for clues.
- `clues` to review unlocked hints.
- `logs` to see your past actions.
- `submit <code>` to try to escape using the final secret code.

## Testing

Run the test suite with pytest:
```bash
pytest tests/
```
