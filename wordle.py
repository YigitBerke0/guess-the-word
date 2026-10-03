import os
import random
import sys
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORDS_FILE = "words.txt"

DEFAULT_WORDS = [
    "APPLE", "BEACH", "BRAIN", "BREAD", "CHAIR", "CHEST", "CLOUD", "DANCE",
    "DREAM", "EARTH", "FRUIT", "GHOST", "GRAPE", "GREEN", "HEART", "HOUSE",
    "JUICE", "LEMON", "LIGHT", "MONEY", "MUSIC", "NIGHT", "OCEAN", "PARTY",
    "PHONE", "PIANO", "PLANT", "QUEEN", "RADIO", "RIVER", "ROBOT", "SHIRT",
    "SMILE", "SNAKE", "SPACE", "STORM", "SUGAR", "TABLE", "TIGER", "TRAIN",
    "WATER", "WHALE", "WHEAT", "WORLD", "YOUTH", "ZEBRA", "SMART", "FLAME",
    "CLOCK", "SPOON", "STAND", "SWEET", "TRACK", "TRUCK", "WATCH", "WHITE",
    "BLACK", "BROWN", "SHINE", "CLEAN", "FRESH", "MAGIC", "PEACE", "POWER",
    "QUIET", "SHARP", "SHOCK", "SOLAR", "SPEED", "TASTE", "TOUCH", "VOICE",
    "BLOOM", "CANDY", "CRANE", "FROST", "HONEY", "LUCKY", "MANGO", "NOBLE"
]

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"

TILE_GREEN = "\033[1;97;42m"    
TILE_YELLOW = "\033[1;30;43m"   
TILE_GRAY = "\033[1;97;100m"    
TILE_EMPTY = "\033[90m"         

COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"
COLOR_GREEN_TXT = "\033[92m"
COLOR_YELLOW_TXT = "\033[93m"


def enable_ansi_support() -> None:
    if sys.platform.startswith("win"):
        os.system("")


def ensure_word_list_file(filepath: str = WORDS_FILE) -> list[str]:
    """
    Checks if the word file exists. If not, automatically creates it and
    populates it with DEFAULT_WORDS. Returns a list of valid 5-letter uppercase words.
    """
    if not os.path.exists(filepath):
        print(f"{COLOR_CYAN}[i] '{filepath}' not found. Generating default word list...{ANSI_RESET}")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for word in sorted(DEFAULT_WORDS):
                    f.write(f"{word}\n")
            print(f"{COLOR_GREEN_TXT}[+] Successfully created '{filepath}' with {len(DEFAULT_WORDS)} words.{ANSI_RESET}\n")
        except OSError as e:
            print(f"{COLOR_RED}[!] Error creating {filepath}: {e}. Falling back to in-memory list.{ANSI_RESET}")
            return list(DEFAULT_WORDS)

    valid_words = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip().upper()
                if len(word) == 5 and word.isalpha():
                    valid_words.append(word)
    except OSError as e:
        print(f"{COLOR_RED}[!] Error reading {filepath}: {e}. Falling back to default list.{ANSI_RESET}")
        return list(DEFAULT_WORDS)

    if not valid_words:
        print(f"{COLOR_RED}[!] Warning: '{filepath}' contained no valid 5-letter words. Using default word list.{ANSI_RESET}")
        return list(DEFAULT_WORDS)

    return valid_words


def evaluate_guess(guess: str, target: str) -> list[str]:
    feedback = [None] * 5
    target_counts = Counter(target)

    for i in range(5):
        if guess[i] == target[i]:
            feedback[i] = "GREEN"
            target_counts[guess[i]] -= 1

    for i in range(5):
        if feedback[i] is None:
            char = guess[i]
            if target_counts[char] > 0:
                feedback[i] = "YELLOW"
                target_counts[char] -= 1
            else:
                feedback[i] = "GRAY"

    return feedback


def render_tile(letter: str, status: str) -> str:
    if status == "GREEN":
        return f"{TILE_GREEN} {letter} {ANSI_RESET}"
    elif status == "YELLOW":
        return f"{TILE_YELLOW} {letter} {ANSI_RESET}"
    elif status == "GRAY":
        return f"{TILE_GRAY} {letter} {ANSI_RESET}"
    else:
        return f"{TILE_EMPTY}[ _ ]{ANSI_RESET}"


def display_board(history: list[tuple[str, list[str]]], max_attempts: int = 6) -> None:
    divider = "=" * 37
    print("\n" + divider)
    for row_idx in range(max_attempts):
        if row_idx < len(history):
            guess_word, feedback = history[row_idx]
            tiles = [render_tile(guess_word[i], feedback[i]) for i in range(5)]
            print(f"  Attempt {row_idx + 1}:  " + " ".join(tiles))
        else:
            empty_tiles = [render_tile("_", "EMPTY") for _ in range(5)]
            print(f"  Attempt {row_idx + 1}:  " + " ".join(empty_tiles))
    print(divider + "\n")


def display_keyboard_status(history: list[tuple[str, list[str]]]) -> None:
    """Displays an A-Z keyboard reference showing the best-known status of each letter."""
    letter_status = {}
    for guess_word, feedback in history:
        for char, status in zip(guess_word, feedback):
            current = letter_status.get(char)
            if current == "GREEN":
                continue
            if status == "GREEN":
                letter_status[char] = "GREEN"
            elif status == "YELLOW" and current != "GREEN":
                letter_status[char] = "YELLOW"
            elif status == "GRAY" and current is None:
                letter_status[char] = "GRAY"

    keyboard_rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    print(f"{ANSI_DIM}Keyboard Status:{ANSI_RESET}")
    for row in keyboard_rows:
        line_parts = []
        for char in row:
            st = letter_status.get(char)
            if st == "GREEN":
                line_parts.append(f"{TILE_GREEN} {char} {ANSI_RESET}")
            elif st == "YELLOW":
                line_parts.append(f"{TILE_YELLOW} {char} {ANSI_RESET}")
            elif st == "GRAY":
                line_parts.append(f"{TILE_GRAY} {char} {ANSI_RESET}")
            else:
                line_parts.append(f"{ANSI_DIM}[{char}]{ANSI_RESET}")
        print("  " + " ".join(line_parts))
    print()


def print_banner() -> None:
    print(f"""{COLOR_CYAN}{ANSI_BOLD}
  +===================================+
  |          TERMINAL WORDLE          |
  +===================================+{ANSI_RESET}
Guess the secret 5-letter word in 6 tries!""")


def get_valid_guess(attempt_num: int, max_attempts: int) -> str:
    while True:
        try:
            raw_input = input(f"Guess {attempt_num}/{max_attempts} > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGame terminated. Goodbye!")
            sys.exit(0)

        if len(raw_input) != 5:
            print(f"{COLOR_RED}[!] Invalid input! Guess must be exactly 5 letters long.{ANSI_RESET}")
            continue

        if not raw_input.isalpha():
            print(f"{COLOR_RED}[!] Invalid input! Guess must contain letters only (A-Z).{ANSI_RESET}")
            continue

        return raw_input.upper()


def play_game(word_pool: list[str], streak: int = 0) -> int:
    """Runs a single round of Wordle. Returns the updated win streak."""
    target_word = random.choice(word_pool).upper()
    max_attempts = 6
    history: list[tuple[str, list[str]]] = []

    print_banner()
    display_board(history, max_attempts)

    won = False
    for attempt in range(1, max_attempts + 1):
        guess = get_valid_guess(attempt, max_attempts)
        feedback = evaluate_guess(guess, target_word)
        history.append((guess, feedback))

        display_board(history, max_attempts)
        display_keyboard_status(history)

        if guess == target_word:
            won = True
            streak += 1
            print(f"{COLOR_GREEN_TXT}{ANSI_BOLD}*** Splendid! You guessed the word '{target_word}' in {attempt}/{max_attempts} attempts! ***{ANSI_RESET}")
            print(f"{COLOR_YELLOW_TXT}{ANSI_BOLD}Current Win Streak: {streak}{ANSI_RESET}\n")
            return streak

    if not won:
        print(f"{COLOR_RED}{ANSI_BOLD}[GAME OVER] You've used all {max_attempts} attempts.{ANSI_RESET}")
        print(f"The secret word was: {COLOR_CYAN}{ANSI_BOLD}{target_word}{ANSI_RESET}\n")
        return 0


def main() -> None:
    enable_ansi_support()
    word_pool = ensure_word_list_file(WORDS_FILE)
    streak = 0

    while True:
        streak = play_game(word_pool, streak)
        
        while True:
            try:
                choice = input("Would you like to play again? (y/n): ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                sys.exit(0)

            if choice in ("y", "yes"):
                print("\n" + "=" * 45 + "\n")
                break
            elif choice in ("n", "no"):
                return
            else:
                print("Please enter 'y' for yes or 'n' for no.")


if __name__ == "__main__":
    main()
