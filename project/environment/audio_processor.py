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
