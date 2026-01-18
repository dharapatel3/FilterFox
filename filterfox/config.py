from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@dataclass
class FilterFoxConfig:
    credentials_path: Path = PROJECT_ROOT / 'credentials.json'
    token_path: Path = PROJECT_ROOT / 'token.json'

    max_results: int = 200
    gmail_query: str = "newer_than:30d in:inbox"

    dry_run: bool = True
    label_prefix: str = "FilterFox"

    #need to keep trash disabled in beta
    allow_trash: bool = False