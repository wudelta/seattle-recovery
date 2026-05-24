# FILE: aurora/tests/__init__.py
# Explicitly expose namespaced test modules to Django's discovery scanner Engine

from .test_session_api import HeadlessSessionAutomationTest
from .test_session_close_api import HeadlessSessionCloseAutomationTest
from .test_minions import MinionArraySecurityTests