import logging
from database import Database
from audio_processor import AudioProcessor
from game_engine import GameEngine
from terminal_ui import TerminalUI
from seed_data import seed_database
from config import DB_PATH

def main():
    # Setup basic logging to file, to keep terminal clean for UI
    logging.basicConfig(
        filename='game.log', 
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize components
    db = Database()
    
    # Check if we need to initialize and seed
    needs_seeding = not DB_PATH.exists()
    
    db.initialize_schema()
    
    if needs_seeding:
        seed_database(db)
        
        # Process audio files
        audio_processor = AudioProcessor(db)
        audio_processor.process_all_stations()
    
    engine = GameEngine(db)
    ui = TerminalUI(engine)
    
    # Start game loop
    ui.start()

if __name__ == "__main__":
    main()
