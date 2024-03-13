from datetime import datetime
from colorama import init, Fore


class Logger:
    def __init__(self):
        init()

    def output(
        self, level: str, color, creator: str, message: str, useUTC: bool = False
    ) -> None:
        # Get time
        time = datetime.utcnow() if useUTC else datetime.now()

        # Add filler
        level = level.rjust(6)

        # Print info
        print(
            f"{Fore.LIGHTBLACK_EX}{time.isoformat()}{Fore.RESET}{color}{level}{Fore.RESET} {Fore.LIGHTBLACK_EX}BIRDFEED:{creator.upper()}:{Fore.RESET} {Fore.LIGHTWHITE_EX}{message}{Fore.RESET}"
        )
