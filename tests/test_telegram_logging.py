import logging
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import logging_utils


class TestTelegramLogging(unittest.TestCase):
    def setUp(self):
        self.root_logger = logging.getLogger()
        self.original_handlers = list(self.root_logger.handlers)
        for handler in list(self.root_logger.handlers):
            if isinstance(handler, logging_utils.TelegramHandler):
                self.root_logger.removeHandler(handler)
        logging_utils.telegram_log_handler = None

    def tearDown(self):
        for handler in list(self.root_logger.handlers):
            if isinstance(handler, logging_utils.TelegramHandler):
                self.root_logger.removeHandler(handler)
        for handler in self.original_handlers:
            if handler not in self.root_logger.handlers:
                self.root_logger.addHandler(handler)
        logging_utils.telegram_log_handler = None

    def test_reconcile_adds_handler_when_enabled_and_configured(self):
        with patch.dict(
            os.environ,
            {
                "TELEGRAM_ENABLED": "true",
                "TELEGRAM_BOT_TOKEN": "123:ABC",
                "TELEGRAM_CHAT_ID": "456",
                "TELEGRAM_LOG_LEVEL": "WARNING",
            },
            clear=False,
        ):
            handler = logging_utils.reconcile_telegram_logging()

        assert isinstance(handler, logging_utils.TelegramHandler)
        assert handler in self.root_logger.handlers
        assert handler.level == logging.WARNING

    def test_reconcile_removes_existing_handler_when_disabled(self):
        existing = logging_utils.TelegramHandler("123:ABC", "456")
        self.root_logger.addHandler(existing)
        logging_utils.telegram_log_handler = existing

        with patch.dict(
            os.environ,
            {
                "TELEGRAM_ENABLED": "false",
                "TELEGRAM_BOT_TOKEN": "123:ABC",
                "TELEGRAM_CHAT_ID": "456",
            },
            clear=False,
        ):
            handler = logging_utils.reconcile_telegram_logging()

        assert handler is None
        assert not any(isinstance(h, logging_utils.TelegramHandler) for h in self.root_logger.handlers)
