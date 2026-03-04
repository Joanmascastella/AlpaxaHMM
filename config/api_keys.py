import os
from dataclasses import dataclass

@dataclass
class ApiKeys:
    fred: str | None = None
    fred_base_url: str | None = 'https://api.stlouisfed.org/fred/series/observations'

    @classmethod
    def from_env(cls) -> "ApiKeys":
        return cls(fred=os.getenv("FRED_API_KEY"))
