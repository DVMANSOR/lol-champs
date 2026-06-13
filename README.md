# lol_champs

**League of Legends Champions & Splash Arts Library**

Scrapes champion data and splash art directly from Riot's official **Data Dragon** CDN. No API key, no rate limiting, no authentication.

```python
from lol_champs import get_all_champions, get_champion

# All 170+ champions
champs = get_all_champions()
for c in champs:
    print(f"{c.name} — {c.title}  [{', '.join(c.tags)}]")

# Single champion with full skins
ahri = get_champion("Ahri")
print(f"{ahri.name} has {len(ahri.skins)} skins")

# Get a splash URL
skin = ahri.skins[0]
print(skin.splash_url)   # full CDN URL

# Download it
skin.download("ahri_default.jpg")
```

## Install

```bash
pip install lol_champs/
# or from within the directory
pip install -e .
```

## API

| Function | Returns | Description |
|---|---|---|
| `get_all_champions()` | `list[Champion]` | All champions (basic data only) |
| `get_all_champions(include_skins=True)` | `list[Champion]` | All champions with full skin lists (slower) |
| `get_champion("Ahri")` | `Champion \| None` | Single champion with all skins |

### Champion

| Attribute | Type | Description |
|---|---|---|
| `.id` | `str` | Internal ID (e.g. `"Aatrox"`) |
| `.name` | `str` | Display name |
| `.title` | `str` | Title line |
| `.tags` | `list[str]` | Roles: Fighter, Mage, Assassin, Tank, Support, Marksman |
| `.skins` | `list[Skin]` | All skins (default + chromas) |
| `.stats` | `dict` | Base stats (hp, armor, attackspeed, movespeed, etc.) |
| `.info` | `dict` | Ratings: attack, defense, magic, difficulty (0–10) |
| `.partype` | `str` | Resource type: Mana, Energy, Blood Well, etc. |
| `.icon_url` | `str` | URL to 48×48 square icon |
| `.default_splash_url` | `str` | URL to default splash art |

### Skin

| Attribute / Method | Returns | Description |
|---|---|---|
| `.name` | `str` | Skin display name |
| `.num` | `int` | Skin number (0 = default) |
| `.splash_url` | `str` | 1920×1080 splash art URL |
| `.loading_url` | `str` | 640×960 loading screen URL |
| `.centered_url` | `str` | Cropped/centered variant URL |
| `.download(path)` | `str` | Download to file |
| `.download_bytes()` | `bytes` | Download into memory |

## Data Source

All data is fetched live from **Riot Games Data Dragon**:
- `https://ddragon.leagueoflegends.com/`
- Data is always the latest patch version
- Results are cached in memory per process

## License

MIT
