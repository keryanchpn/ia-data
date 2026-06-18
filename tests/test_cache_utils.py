import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cache_utils import get_json_with_cache


class CacheUtilsTest(unittest.TestCase):
    def test_reuses_cached_json_until_refresh_is_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = {"count": 0}

            def fetch_json():
                calls["count"] += 1
                return {"value": calls["count"]}

            first = get_json_with_cache("mitre", "CVE-2026-0001", fetch_json, cache_root=tmp)
            second = get_json_with_cache("mitre", "CVE-2026-0001", fetch_json, cache_root=tmp)
            refreshed = get_json_with_cache(
                "mitre", "CVE-2026-0001", fetch_json, cache_root=tmp, refresh_cache=True
            )

            self.assertEqual(first, {"value": 1})
            self.assertEqual(second, {"value": 1})
            self.assertEqual(refreshed, {"value": 2})
            self.assertEqual(calls["count"], 2)

    def test_falls_back_to_existing_cache_when_fetch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            cached = get_json_with_cache("epss", "CVE-2026-0002", lambda: {"epss": "0.9"}, cache_root=tmp)

            def broken_fetch():
                raise RuntimeError("network unavailable")

            fallback = get_json_with_cache("epss", "CVE-2026-0002", broken_fetch, cache_root=tmp)

            self.assertEqual(cached, {"epss": "0.9"})
            self.assertEqual(fallback, {"epss": "0.9"})


if __name__ == "__main__":
    unittest.main()
