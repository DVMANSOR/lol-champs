"""Data models for League of Legends champions and their skins."""

from __future__ import annotations

import io
import os
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CDN_BASE = "https://ddragon.leagueoflegends.com/cdn"
SPLASH_BASE = f"{CDN_BASE}/img/champion/splash"
LOADING_BASE = f"{CDN_BASE}/img/champion/loading"
ICON_BASE = f"{CDN_BASE}/img/champion"

# ---------------------------------------------------------------------------
# Skin
# ---------------------------------------------------------------------------


@dataclass
class Skin:
    """A single champion skin with splash art info."""

    name: str
    """Display name of the skin (e.g. 'Dynasty Ahri')."""

    num: int
    """Skin number — used in the CDN URL (0 = default)."""

    champion_id: str
    """Champion ID string (e.g. 'Ahri')."""

    has_splash: bool = True
    """Whether the splash image actually exists on the CDN."""

    # ------------------------------------------------------------------
    # URL generation
    # ------------------------------------------------------------------

    @property
    def splash_url(self) -> str:
        """Full CDN URL to the splash art (1920×1080)."""
        return f"{SPLASH_BASE}/{self.champion_id}_{self.num}.jpg"

    @property
    def loading_url(self) -> str:
        """Full CDN URL to the loading-screen art (640×960)."""
        return f"{LOADING_BASE}/{self.champion_id}_{self.num}.jpg"

    @property
    def centered_url(self) -> str:
        """Full CDN URL to the centered/cropped splash variant."""
        return f"{SPLASH_BASE}/{self.champion_id}_{self.num}_centered.jpg"

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    def download(
        self,
        path: str,
        variant: str = "splash",
        *,
        session=None,
    ) -> str:
        """Download this skin's artwork to *path*.

        Parameters
        ----------
        path:
            Local file path to write to. Parent directories are created
            automatically.
        variant:
            One of ``"splash"`` (default, 1920×1080), ``"loading"``
            (640×960 loading screen), or ``"centered"`` (cropped splash).
        session:
            Optional ``requests.Session`` for connection reuse.

        Returns
        -------
        The absolute path of the downloaded file.
        """
        import requests

        url_map = {
            "splash": self.splash_url,
            "loading": self.loading_url,
            "centered": self.centered_url,
        }
        url = url_map[variant]
        sess = session or requests.Session()

        path = os.path.abspath(path)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        resp = sess.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        return path

    def download_bytes(self, variant: str = "splash", *, session=None) -> bytes:
        """Download this skin's artwork into memory and return the bytes."""
        import requests

        url_map = {
            "splash": self.splash_url,
            "loading": self.loading_url,
            "centered": self.centered_url,
        }
        url = url_map[variant]
        sess = session or requests.Session()
        resp = sess.get(url, timeout=30)
        resp.raise_for_status()
        return resp.content

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<Skin '{self.name}' [{self.champion_id}_{self.num}]>"
        )


# ---------------------------------------------------------------------------
# Champion
# ---------------------------------------------------------------------------


@dataclass
class Champion:
    """A League of Legends champion with stats, tags, and skin data."""

    id: str
    """CDN / internal ID (e.g. 'Aatrox')."""

    key: str
    """Numeric champion key (e.g. '266')."""

    name: str
    """Display name (e.g. 'Aatrox')."""

    title: str
    """Title line (e.g. 'the Darkin Blade')."""

    blurb: str
    """Short lore description."""

    tags: list[str] = field(default_factory=list)
    """Role tags: 'Fighter', 'Mage', 'Assassin', 'Tank', 'Support', 'Marksman'."""

    info: dict = field(default_factory=dict)
    """Rating dict with keys ``attack``, ``defense``, ``magic``, ``difficulty`` (0-10)."""

    stats: dict = field(default_factory=dict)
    """Base stats dict (hp, mp, armor, attackspeed, movespeed, …)."""

    partype: str = ""
    """Resource type: 'Mana', 'Blood Well', 'Energy', 'Fury', 'Heat', etc."""

    skins: list[Skin] = field(default_factory=list)
    """All available skins, including the default (skin num 0)."""

    version: str = ""
    """Data Dragon version these values came from."""

    # ------------------------------------------------------------------
    # URL generation
    # ------------------------------------------------------------------

    @property
    def icon_url(self) -> str:
        """URL to the champion's square icon (48×48)."""
        return f"{ICON_BASE}/{self.id}.png"

    @property
    def default_splash_url(self) -> str:
        """URL to the default (skin 0) splash art."""
        return f"{SPLASH_BASE}/{self.id}_0.jpg"

    @property
    def default_loading_url(self) -> str:
        """URL to the default (skin 0) loading screen art."""
        return f"{LOADING_BASE}/{self.id}_0.jpg"

    # ------------------------------------------------------------------
    # Downloads
    # ------------------------------------------------------------------

    def download_default_splash(self, path: str, *, session=None) -> str:
        """Download the default splash art."""
        return self.skins[0].download(path, "splash", session=session)

    def download_all_splashes(
        self,
        directory: str,
        variant: str = "splash",
        *,
        session=None,
        progress: bool = True,
    ) -> list[str]:
        """Download every skin's artwork into *directory*.

        Returns a list of absolute file paths that were written.
        """
        import requests

        sess = session or requests.Session()
        out = []
        directory = os.path.abspath(directory)
        os.makedirs(directory, exist_ok=True)

        for skin in self.skins:
            if not skin.has_splash:
                continue
            ext = ".jpg"
            fname = f"{self.id}_{skin.num}_{skin.name.replace('/', '_')}{ext}"
            # sanitize filename
            fname = "".join(c if c.isalnum() or c in "._- " else "_" for c in fname)
            dst = os.path.join(directory, fname)
            try:
                skin.download(dst, variant, session=sess)
                out.append(dst)
                if progress:
                    print(f"  ✓ {skin.name}")
            except Exception as exc:
                if progress:
                    print(f"  ✗ {skin.name} — {exc}")

        return out

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def skin_by_name(self, name: str) -> Optional[Skin]:
        """Look up a skin by its display name (case-insensitive, partial match)."""
        name_lower = name.lower()
        for skin in self.skins:
            if name_lower in skin.name.lower():
                return skin
        return None

    def skin_by_num(self, num: int) -> Optional[Skin]:
        """Look up a skin by its numeric index."""
        for skin in self.skins:
            if skin.num == num:
                return skin
        return None

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        tags = ", ".join(self.tags)
        return (
            f"<Champion {self.name} — '{self.title}' [{tags}] "
            f"({len(self.skins)} skins)>"
        )
