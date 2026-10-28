"""Fake HTTP session for fetch tests (no network)."""

import json


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=None, headers=None):
        self.status_code = status_code
        self._payload = payload
        if text is None and payload is not None:
            text = json.dumps(payload)
        self.text = text or ""
        self.content = self.text.encode("utf-8")
        self.headers = headers or {}

    def json(self):
        if self._payload is None:
            return json.loads(self.text)
        return self._payload


class FakeSession:
    """Answers each GET with handler(url, params) and records all calls."""

    def __init__(self, handler):
        self.handler = handler
        self.calls: list[tuple[str, dict]] = []

    def get(self, url, params=None, **kwargs):
        params = dict(params or {})
        self.calls.append((url, params))
        result = self.handler(url, params)
        if isinstance(result, Exception):
            raise result
        return result


def point_feature(x, y, **props):
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [x, y]}, "properties": props}
