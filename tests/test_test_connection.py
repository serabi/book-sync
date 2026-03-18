"""Tests for the diagnostic test-connection endpoint."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.blueprints.settings_bp import (
    _test_abs,
    _test_conn_error,
    _test_hardcover,
    _test_kosync,
    _test_storyteller,
    _test_telegram,
)


class TestConnErrorHelper(unittest.TestCase):
    def test_connection_refused(self):
        err = ConnectionError("Connection refused")
        result = _test_conn_error(err)
        assert "Connection refused" in result

    def test_timeout(self):
        from requests.exceptions import Timeout
        err = Timeout("timed out")
        result = _test_conn_error(err)
        assert "timed out" in result.lower()

    def test_generic_error(self):
        err = Exception("something weird")
        result = _test_conn_error(err)
        assert "something weird" in result


class TestAbsConnection(unittest.TestCase):
    def test_missing_config(self):
        with patch.dict(os.environ, {'ABS_SERVER': '', 'ABS_KEY': ''}, clear=False):
            ok, detail = _test_abs()
            assert not ok
            assert 'not configured' in detail.lower()

    @patch('src.blueprints.settings_bp.http_requests.get')
    def test_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'username': 'admin'}
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {'ABS_SERVER': 'http://abs:13378', 'ABS_KEY': 'tok123'}):
            ok, detail = _test_abs()
            assert ok
            assert 'admin' in detail

    @patch('src.blueprints.settings_bp.http_requests.get')
    def test_failure(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {'ABS_SERVER': 'http://abs:13378', 'ABS_KEY': 'badtoken'}):
            ok, detail = _test_abs()
            assert not ok
            assert '401' in detail


class TestStorytellerConnection(unittest.TestCase):
    def test_missing_config(self):
        with patch.dict(os.environ, {'STORYTELLER_API_URL': '', 'STORYTELLER_USER': '', 'STORYTELLER_PASSWORD': ''}, clear=False):
            ok, detail = _test_storyteller()
            assert not ok

    @patch('src.blueprints.settings_bp.http_requests.post')
    def test_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        with patch.dict(os.environ, {
            'STORYTELLER_API_URL': 'http://st:8001',
            'STORYTELLER_USER': 'user',
            'STORYTELLER_PASSWORD': 'pass',
        }):
            ok, detail = _test_storyteller()
            assert ok
            assert 'Authenticated' in detail


class TestTelegramConnection(unittest.TestCase):
    def test_missing_token(self):
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': ''}, clear=False):
            ok, detail = _test_telegram()
            assert not ok
            assert 'not configured' in detail.lower()

    def test_missing_chat_id(self):
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': '123:ABC', 'TELEGRAM_CHAT_ID': ''}, clear=False):
            ok, detail = _test_telegram()
            assert not ok
            assert 'chat id' in detail.lower()

    @patch('src.blueprints.settings_bp.http_requests.post')
    @patch('src.blueprints.settings_bp.http_requests.get')
    def test_success(self, mock_get, mock_post):
        me_resp = MagicMock()
        me_resp.status_code = 200
        me_resp.json.return_value = {'result': {'first_name': 'SyncBot'}}
        mock_get.return_value = me_resp

        send_resp = MagicMock()
        send_resp.status_code = 200
        mock_post.return_value = send_resp

        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': '123:ABC', 'TELEGRAM_CHAT_ID': '456'}):
            ok, detail = _test_telegram()
            assert ok
            assert 'SyncBot' in detail
            mock_post.assert_called_once()

    @patch('src.blueprints.settings_bp.http_requests.post')
    @patch('src.blueprints.settings_bp.http_requests.get')
    def test_send_failure_returns_telegram_description(self, mock_get, mock_post):
        me_resp = MagicMock()
        me_resp.status_code = 200
        me_resp.json.return_value = {'result': {'first_name': 'SyncBot'}}
        mock_get.return_value = me_resp

        send_resp = MagicMock()
        send_resp.status_code = 400
        send_resp.json.return_value = {'description': 'Bad Request: chat not found'}
        mock_post.return_value = send_resp

        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': '123:ABC', 'TELEGRAM_CHAT_ID': '456'}):
            ok, detail = _test_telegram()
            assert not ok
            assert 'chat not found' in detail.lower()


class TestHardcoverConnection(unittest.TestCase):
    def test_missing_token(self):
        with patch.dict(os.environ, {'HARDCOVER_TOKEN': ''}, clear=False):
            ok, detail = _test_hardcover()
            assert not ok

    @patch('src.blueprints.settings_bp.http_requests.post')
    def test_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'data': {'me': {'id': 1, 'username': 'reader'}}}
        mock_post.return_value = mock_resp

        with patch.dict(os.environ, {'HARDCOVER_TOKEN': 'hc_tok'}):
            ok, detail = _test_hardcover()
            assert ok
            assert 'reader' in detail


if __name__ == '__main__':
    unittest.main()
