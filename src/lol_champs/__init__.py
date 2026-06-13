"""
lol_champs — League of Legends Champions & Splash Arts Library.

Scrapes champion data and splash art from Riot's official Data Dragon CDN.
No API key required. All data is fetched live from ddragon.leagueoflegends.com.

Usage:
    from lol_champs import get_all_champions, get_champion, Champion

    # List all 170+ champions
    champs = get_all_champions()
    for c in champs:
        print(c.name, c.title, c.tags)

    # Get one champion with full skin info
    ahri = get_champion("Ahri")
    print(ahri.skins[1].name)       # "Dynasty Ahri"
    print(ahri.skins[1].splash_url) # direct CDN URL

    # Download a splash art
    ahri.skins[0].download("ahri_default.jpg")
"""

from lol_champs._client import (
    get_all_champions,
    get_champion,
    fetch_latest_version,
)
from lol_champs._models import Champion, Skin

__all__ = [
    "get_all_champions",
    "get_champion",
    "fetch_latest_version",
    "Champion",
    "Skin",
]
