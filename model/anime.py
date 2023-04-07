from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class Anime:
    trailer_url: str
    url: str
    title: str
    _type: str
    episodes: int
    airing: bool
    score: float
    rank: int
    popularity: int
    members: int
    favorites: int
    synopsis: str
    year: int
    genres: List[str]
    theme: str
    streaming: str

    def to_dict(self):
        return asdict(self)
