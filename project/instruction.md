# Terminal Radio Escape Puzzle

The game requires players to scan for available radio frequencies, tune to them to retrieve clues based on audio metadata, and track their progress toward escape using a final code.

The system relies on a local SQLite database and requires implementing specific classes and methods across several Python modules: `Database`, `GameEngine`, `AudioProcessor`, and `TerminalUI`.

### Deliverable Constraints
- Your implementation will be verified by a hidden automated test suite.
- Ensure all specified behaviors, schemas, and output formats are implemented exactly as described below.

### Database Schema Requirements
The application must use an SQLite database with the following specific tables and constraints:
- **`stations`**: Must contain at least `id`, `name`, `frequency`, and `audio_file` columns. The `frequency` column MUST have a `NOT NULL` constraint and a `UNIQUE` constraint.
- **`audio_metadata`**: Must contain at least `id`, `station_id`, `duration`, `peak_volume`, `sample_rate`, and `bitrate` columns.
- **`clues`**: Must contain at least `id`, `station_id`, and `message` columns.

### Component Behaviors
1. **GameEngine**
   - Track actions in an internal log.
   - `scan_stations()`: Return a list of available frequencies and log the exact message: `"Player scanned for stations."`
   - `tune(frequency)`: If the frequency is valid, connect to it, unlock its clue, log `"Player tuned to {name} ({freq})."`, log `"Player discovered a clue on {name}."`, and return a string containing `"Connected to {name}"`. If invalid, return a string containing `"Static noise... No station found at this frequency."`
   - `submit_code(code)`: Evaluate the code against the `FINAL_CODE` variable imported from `config.py`. Return `True` on a match, `False` otherwise. It must also log `"Player submitted escape code: {code}"`.

2. **TerminalUI**
   Must implement specific commands that print exact substrings:
   - `help`: Must output a string containing `"Available commands"` and list commands like `scan` and `tune`.
   - `scan`: Output must contain the exact header `"Available Stations:"` and format frequencies as `"{freq} FM"` (e.g., `"101.1 FM"`).
   - `tune {freq}`: Connects the radio. Outputs `"Connected to {name}"` on success.
   - `logs`: Outputs the action history exactly as logged by the GameEngine.
   - `clues`: Displays the unlocked clues.
   - `status`: Must output `"Radio is off"` when not tuned to anything, or `"Currently tuned to: {name}"` when tuned.
   - `submit {code}`: Must output `"You Escaped!"` if the code is correct, and `"Access Denied"` if incorrect.

3. **AudioProcessor**
   - Uses `ffmpeg`/`ffprobe` to analyze local `.wav` files.
   - `extract_metadata(filename)`: Extract `sample_rate` (int), `duration` (float), and `bitrate` (int) from the file.
   - `extract_peak_volume(filename)`: Extract peak volume (float) from the file using an `ffmpeg` `volumedetect` filter.
   - `process_all_stations()`: Iterates through all stations in the database, extracts their audio metadata, and stores it in the `audio_metadata` table. Handle missing files gracefully without crashing.
