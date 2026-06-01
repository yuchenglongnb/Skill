"""Low-frequency HTTP fetching without browser automation."""

from __future__ import annotations

import time
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import requests

from tgb_pipeline.config import CrawlSettings


class Fetcher:
    def __init__(self, settings: CrawlSettings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.user_agent})
        self._last_request_at: float | None = None
        self._robots: dict[str, RobotFileParser | None] = {}

    def get_text(self, url: str) -> str:
        self._assert_allowed(url)
        last_error: requests.RequestException | None = None
        for attempt in range(self.settings.max_retries + 1):
            self._wait_for_interval()
            try:
                response = self.session.get(
                    url,
                    timeout=self.settings.request_timeout_seconds,
                )
                self._last_request_at = time.monotonic()
                response.raise_for_status()
                if response.encoding is None:
                    response.encoding = response.apparent_encoding
                return response.text
            except requests.RequestException as exc:
                self._last_request_at = time.monotonic()
                last_error = exc
                if attempt >= self.settings.max_retries:
                    raise
        raise RuntimeError("unreachable") from last_error

    def _wait_for_interval(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        remaining = self.settings.request_interval_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def _assert_allowed(self, url: str) -> None:
        if not self.settings.respect_robots_txt:
            return
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self._robots:
            self._robots[origin] = self._load_robots(origin)
        parser = self._robots[origin]
        if parser is not None and not parser.can_fetch(self.settings.user_agent, url):
            raise PermissionError(f"robots.txt disallows fetching: {url}")

    def _load_robots(self, origin: str) -> RobotFileParser | None:
        robots_url = urljoin(origin, "/robots.txt")
        self._wait_for_interval()
        try:
            response = self.session.get(
                robots_url,
                timeout=self.settings.request_timeout_seconds,
            )
            self._last_request_at = time.monotonic()
            if response.status_code >= 400:
                return None
            parser = RobotFileParser()
            parser.set_url(robots_url)
            parser.parse(response.text.splitlines())
            return parser
        except requests.RequestException:
            self._last_request_at = time.monotonic()
            return None

