"""Tests for Booklore cover proxy endpoint and auth contract."""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.blueprints.covers import _proxy_booklore_cover_for  # noqa: E402


class TestBookloreCoverProxy(unittest.TestCase):
    """Verify _proxy_booklore_cover_for sends correct URL, auth, and headers."""

    def _make_client(self, configured=True, token='fake-jwt-token'):
        client = Mock()
        client.is_configured.return_value = configured
        client.base_url = 'http://booklore.local'
        client._get_fresh_token.return_value = token
        return client

    # ── URL and auth contract ──────────────────────────────────────

    @patch('src.blueprints.covers.requests.get')
    def test_uses_media_endpoint_path(self, mock_get):
        """API path must be /api/v1/media/book/{id}/cover."""
        mock_get.return_value = Mock(status_code=404)
        bl = self._make_client()

        _proxy_booklore_cover_for(bl, 3880)

        called_url = mock_get.call_args[0][0]
        self.assertEqual(called_url, 'http://booklore.local/api/v1/media/book/3880/cover')

    @patch('src.blueprints.covers.requests.get')
    def test_auth_via_query_param_not_header(self, mock_get):
        """JWT must be sent as ?token= query param, not Authorization header."""
        mock_get.return_value = Mock(status_code=404)
        bl = self._make_client(token='my-secret-jwt')

        _proxy_booklore_cover_for(bl, 42)

        kwargs = mock_get.call_args[1]
        self.assertEqual(kwargs['params'], {'token': 'my-secret-jwt'})
        self.assertNotIn('headers', kwargs,
                         'Should not send Authorization header — Booklore media uses query-param auth')

    # ── Response contract ──────────────────────────────────────────

    @patch('src.blueprints.covers.requests.get')
    def test_content_type_hardcoded_jpeg(self, mock_get):
        """Response must be image/jpeg regardless of upstream Content-Type."""
        upstream = Mock(status_code=200)
        upstream.headers = {'content-type': 'application/json'}
        upstream.iter_content.return_value = iter([b'\xff\xd8\xff\xe0'])
        mock_get.return_value = upstream
        bl = self._make_client()

        resp = _proxy_booklore_cover_for(bl, 1)

        self.assertEqual(resp.content_type, 'image/jpeg')

    @patch('src.blueprints.covers.requests.get')
    def test_cache_control_header_set(self, mock_get):
        """Successful proxy response must set long-lived cache headers."""
        upstream = Mock(status_code=200)
        upstream.iter_content.return_value = iter([b'imgdata'])
        mock_get.return_value = upstream
        bl = self._make_client()

        resp = _proxy_booklore_cover_for(bl, 1)

        self.assertEqual(resp.headers.get('Cache-Control'), 'public, max-age=86400, immutable')

    @patch('src.blueprints.covers.requests.get')
    def test_streams_upstream_body(self, mock_get):
        """Proxy must stream the upstream body content through."""
        chunks = [b'chunk1', b'chunk2']
        upstream = Mock(status_code=200)
        upstream.iter_content.return_value = iter(chunks)
        mock_get.return_value = upstream
        bl = self._make_client()

        resp = _proxy_booklore_cover_for(bl, 1)

        body = b''.join(resp.response)
        self.assertEqual(body, b'chunk1chunk2')

    # ── Error paths ────────────────────────────────────────────────

    def test_not_configured_returns_404(self):
        bl = self._make_client(configured=False)
        result = _proxy_booklore_cover_for(bl, 1)
        self.assertEqual(result, ("Booklore not configured", 404))

    def test_auth_failure_returns_500(self):
        bl = self._make_client(token=None)
        result = _proxy_booklore_cover_for(bl, 1)
        self.assertEqual(result, ("Booklore auth failed", 500))

    @patch('src.blueprints.covers.requests.get')
    def test_upstream_404_returns_404(self, mock_get):
        mock_get.return_value = Mock(status_code=404)
        bl = self._make_client()
        result = _proxy_booklore_cover_for(bl, 9999)
        self.assertEqual(result, ("Cover not found", 404))

    @patch('src.blueprints.covers.requests.get')
    def test_network_error_returns_500(self, mock_get):
        mock_get.side_effect = ConnectionError("refused")
        bl = self._make_client()
        result = _proxy_booklore_cover_for(bl, 1)
        self.assertEqual(result, ("Error loading cover", 500))


if __name__ == '__main__':
    unittest.main()
