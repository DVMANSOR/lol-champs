"""Data-fetching layer — scrapes Riot's Data Dragon CDN."""

from __future__ import annotations

import functools
from typing import Optional

import requests

from lol_champs._models import CDN_BASE, Champion, Skin

# ---------------------------------------------------------------------------
# Low-level
# ---------------------------------------------------------------------------

_SESSION: requests.Session | None = None


def _get_session() -> requests.Session:
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
        _SESSION.headers.update(
            {
                "User-Agent": (
                    "lol_champs/1.0 (+https://github.com/your-username/lol_champs)"
                ),
                "Accept": "application/json, image/*",
            }
        )
    return _SESSION


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------


@functools.lru_cache(maxsize=1)
def fetch_latest_version() -> str:
    """Return the latest Data Dragon version string (e.g. ``"16.12.1"``).

    Results are cached in memory for the lifetime of the process.
    """
    sess = _get_session()
    resp = sess.get(
        "https://ddragon.leagueoflegends.com/api/versions.json",
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()[0]


# ---------------------------------------------------------------------------
# Champion fetching
# ---------------------------------------------------------------------------


@functools.lru_cache(maxsize=1)
def _fetch_champion_list_json(
    version: Optional[str] = None,
) -> tuple[str, dict]:
    """Fetch the full champion list JSON, return ``(version, data_dict)``."""
    v = version or fetch_latest_version()
    sess = _get_session()
    url = f"{CDN_BASE}/{v}/data/en_US/champion.json"
    resp = sess.get(url, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    return payload["version"], payload["data"]


def _fetch_champion_detail_json(
    champion_id: str,
    version: Optional[str] = None,
) -> dict:
    """Fetch detailed data for a single champion (includes skins)."""
    v = version or fetch_latest_version()
    sess = _get_session()
    url = f"{CDN_BASE}/{v}/data/en_US/champion/{champion_id}.json"
    resp = sess.get(url, timeout=15)
    resp.raise_for_status()
    payload = resp.json()
    return payload["data"][champion_id]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_all_champions(
    *,
    version: Optional[str] = None,
    include_skins: bool = False,
) -> list[Champion]:
    """Fetch all champions from the Data Dragon CDN.

    Parameters
    ----------
    version:
        A specific Data Dragon version string. When ``None`` (default) the
        latest available version is used automatically.
    include_skins:
        If ``True``, each champion's full skin list is fetched individually
        (slower but gives you all skin data upfront). If ``False``, only
        the default ``Skin(num=0)`` is populated.

    Returns
    -------
    A list of :class:`Champion` objects sorted alphabetically by ``id``.
    """
    ver, raw_data = _fetch_champion_list_json(version)

    champs: list[Champion] = []
    for champ_id, raw in raw_data.items():
        # basic fields (available in the list endpoint)
        skin_default = Skin(
            name="default",
            num=0,
            champion_id=champ_id,
        )
        c = Champion(
            id=raw["id"],
            key=raw["key"],
            name=raw["name"],
            title=raw["title"],
            blurb=raw.get("blurb", ""),
            tags=raw.get("tags", []),
            info=raw.get("info", {}),
            stats=raw.get("stats", {}),
            partype=raw.get("partype", ""),
            skins=[skin_default],
            version=ver,
        )

        if include_skins:
            detail = _fetch_champion_detail_json(champ_id, version=ver)
            c.skins = _build_skins(detail)

        champs.append(c)

    champs.sort(key=lambda c: c.id.lower())
    return champs


def get_champion(
    name_or_id: str,
    *,
    version: Optional[str] = None,
) -> Optional[Champion]:
    """Fetch a single champion by name or ID (case-insensitive).

    Parameters
    ----------
    name_or_id:
        Champion name or ID, e.g. ``"Ahri"``, ``"Jarvan IV"``.
    version:
        Optional specific Data Dragon version.

    Returns
    -------
    A fully populated :class:`Champion` (with skins), or ``None`` if no
    champion matches.
    """
    v = version or fetch_latest_version()

    # Try to look up the champion ID from the list first (case-insensitive)
    _, raw_data = _fetch_champion_list_json(v)
    champ_id = _match_champion_id(name_or_id, raw_data)
    if champ_id is None:
        return None

    detail = _fetch_champion_detail_json(champ_id, version=v)
    raw = raw_data[champ_id]

    skins = _build_skins(detail)
    c = Champion(
        id=raw["id"],
        key=raw["key"],
        name=raw["name"],
        title=raw["title"],
        blurb=raw.get("blurb", ""),
        tags=raw.get("tags", []),
        info=raw.get("info", {}),
        stats=raw.get("stats", {}),
        partype=raw.get("partype", ""),
        skins=skins,
        version=v,
    )
    return c


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _match_champion_id(query: str, raw_data: dict) -> Optional[str]:
    """Case-insensitive prefix / exact match against champion names/IDs."""
    q = query.strip().lower()
    # exact match on id
    if q in raw_data:
        return q
    # exact match on name
    for cid, info in raw_data.items():
        if info["name"].lower() == q:
            return cid
    # prefix match
    for cid, info in raw_data.items():
        if cid.lower().startswith(q) or info["name"].lower().startswith(q):
            return cid
    return None


def _build_skins(detail: dict) -> list[Skin]:
    """Build Skin objects from a champion detail dict."""
    raw_skins = detail.get("skins", [])
    if not raw_skins:
        return [
            Skin(name="default", num=0, champion_id=detail["id"])
        ]
    skins = []
    for s in raw_skins:
        skins.append(
            Skin(
                name=s["name"],
                num=s["num"],
                champion_id=detail["id"],
                has_splash=(s.get("id") != "0" or True),
            )
        )
    # Chromas can push skin numbers high — deduplicate by num
    seen: set[int] = set()
    deduped: list[Skin] = []
    for sk in skins:
        if sk.num not in seen:
            seen.add(sk.num)
            deduped.append(sk)
    deduped.sort(key=lambda s: s.num)
    return deduped
