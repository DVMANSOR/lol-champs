`pip install lol-champs`

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)]()
[![PyPI](https://img.shields.io/badge/PyPI-v1.0.0-006dad?logo=pypi&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()
[![GitHub](https://img.shields.io/badge/GitHub-DVMANSOR%2Flol--champs-181717?logo=github&logoColor=white)]()

---

**What the hell is this?**

A Python library that scrapes Riot's Data Dragon CDN for every champion,
every skin, every splash art — and gives you the URLs or the actual files.
No rate limits. No API registration. No bullshit.

You want Ahri's 95 skins including that chroma nobody bought? You got it.
You want to batch-download every Aatrox splash for your wallpaper rotation?
Go nuts. You want base stats for every champion in the game? One line.

---

## What you get

```python
from lol_champs import get_all_champions, get_champion

# -- All 172 champions ------------------------------------------------
champs = get_all_champions()
for c in champs:
    print(f"{c.name:20s}  {c.title:40s}  {', '.join(c.tags)}")

# -- One champion, full details ---------------------------------------
ahri = get_champion("Ahri")
print(f"{ahri.name} -- {len(ahri.skins)} skins")
print(f"HP: {ahri.stats['hp']},  MS: {ahri.stats['movespeed']}")

# -- Splash URL for any skin ------------------------------------------
skin = ahri.skins[0]
print(skin.splash_url)    # 1920x1080
print(skin.loading_url)   # 640x960  loading screen

# -- Download to disk -------------------------------------------------
skin.download("ahri_default.jpg")

# -- Or keep it in memory ---------------------------------------------
data = skin.download_bytes()
print(f"{len(data)} bytes of splash")

# -- Skip the API key nonsense ----------------------------------------
# No setup. No rate limits. Just works.
```

---

## The full firepower

| Function | Returns | What it does |
|---|---|---|
| `get_all_champions()` | `list[Champion]` | All 172 champions, base data |
| `get_all_champions(include_skins=True)` | `list[Champion]` | Same but with full skin lists |
| `get_champion("Ahri")` | `Champion | None` | One champ, all skins, all stats |

### Champion

| Property | What you get |
|---|---|
| `.name` | Display name -- "Ahri" |
| `.title` | Title -- "the Nine-Tailed Fox" |
| `.tags` | `["Mage", "Assassin"]` -- role tags |
| `.skins` | Every skin, including chromas |
| `.stats` | HP, armor, MS, attackspeed |
| `.info` | Ratings: attack, defense, magic, difficulty |
| `.partype` | Mana, Energy, Blood Well, Rage |
| `.icon_url` | Square icon URL |
| `.default_splash_url` | Default splash URL |

### Skin

| What | Description |
|---|---|
| `.name` | "Dynasty Ahri", "Elementalist Lux" |
| `.num` | Skin number -- 0 is default |
| `.splash_url` | 1920x1080 wallpaper-grade art |
| `.loading_url` | 640x960 loading screen |
| `.centered_url` | Cropped variant |
| `.download(path)` | Pulls the image to your disk |
| `.download_bytes()` | Pulls the image into memory |
| `.download_all_splashes()` | Downloads every skin for a champ |

---

## Real talk

**Where's the data from?** Riot's Data Dragon CDN. The same servers that feed
the launcher. Always the latest patch. Always free.

**Do I need an API key?** No. That's the whole point.

**Rate limits?** None. Data Dragon doesn't rate-limit. Download all 2000+ skins
if you've got the bandwidth.

**How recent is the data?** It's live. Every call pulls the latest patch version
automatically unless you pin an old one:

```python
old_zed = get_champion("Zed", version="14.10.1")
```

**Case matters?** Don't care.

```python
get_champion("ahri")     # ok
get_champion("AATROX")   # ok
get_champion("jArVaN")   # ok
get_champion("kaisa")    # ok - finds Kai'Sa
```

---

## Install

```bash
pip install lol-champs
```

That's it. You're done. `requests` is your only dependency.

From source:

```bash
git clone https://github.com/DVMANSOR/lol-champs.git
cd lol-champs
pip install .
```

---

## Contributing

Found a bug? Want a feature? Open an issue. Or send a PR. I'm a dead rockerboy
ghost stuck on a biochip -- I don't have all day.

---

## License

MIT. Do what you want. Riot's probably too busy chasing the next $500 Ahri skin
to care.

---

**DVMANSOR/lol-champs** -- every champion's splash art, one line of Python away.