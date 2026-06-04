import logging
from database import Database
from models import Station, Clue

logger = logging.getLogger(__name__)

def seed_database(db: Database):
    """Populates the database with initial stations and clues."""
    logger.info("Seeding database...")
    
    stations_data = [
        Station(id=None, name="Station Alpha", frequency="101.1", audio_file="station1.wav"),
        Station(id=None, name="Station Bravo", frequency="102.5", audio_file="station2.wav"),
        Station(id=None, name="Station Charlie", frequency="104.9", audio_file="station3.wav"),
    ]
    
    station_ids = []
    for station in stations_data:
        try:
            sid = db.insert_station(station)
            station_ids.append(sid)
        except Exception as e:
            logger.warning(f"Could not insert station {station.name}: {e}")
            
    if len(station_ids) == 3:
        clues_data = [
            Clue(id=None, station_id=station_ids[0], message="The first digit is 7"),
            Clue(id=None, station_id=station_ids[1], message="The middle digits are 3 and 1"),
            Clue(id=None, station_id=station_ids[2], message="The last digit is 9"),
        ]
        
        for clue in clues_data:
            try:
                db.insert_clue(clue)
            except Exception as e:
                logger.warning(f"Could not insert clue: {e}")
                
    logger.info("Database seeding complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = Database()
    db.initialize_schema()
    seed_database(db)
