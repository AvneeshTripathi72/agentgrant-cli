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
