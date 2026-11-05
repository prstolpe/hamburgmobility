"""HTTP access for the fetch stage. Errors raise FetchError; there are no fallback URLs."""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENT = "hh-strassenfunktionsplan/0.1 (nicht amtlicher Entwurf; Datenabruf Hamburg)"
TIMEOUT_S = 60


class FetchError(RuntimeError):
    """A source could not be fetched or failed a consistency check."""


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    retry = Retry(total=2, backoff_factor=2, status_forcelist=[502, 503, 504], allowed_methods=["GET"])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def get(session, url: str, params: dict | None = None, **kwargs):
    """GET that raises FetchError on network errors and on any status other than 200."""
    kwargs.setdefault("timeout", TIMEOUT_S)
    try:
        response = session.get(url, params=params, **kwargs)
    except requests.RequestException as exc:
        raise FetchError(f"{url}: {exc}") from exc
    if response.status_code != 200:
        raise FetchError(f"{url}: HTTP {response.status_code}")
    return response


def get_json(session, url: str, params: dict | None = None, **kwargs):
    """GET and parse JSON; a broken or truncated body raises FetchError."""
    response = get(session, url, params=params, **kwargs)
    try:
        return response.json()
    except ValueError as exc:
        raise FetchError(f"{url}: invalid JSON after {len(response.content)} bytes ({exc})") from exc
