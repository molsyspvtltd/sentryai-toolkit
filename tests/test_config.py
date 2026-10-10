
import pytest

from toolkit.config import SentryAIConfig


def test_valid_local_target_is_accepted():
    config = SentryAIConfig(
        target_url="http://127.0.0.1:8080",
        testing_scope="local-dvwa",
    )
    config.validate()


def test_localhost_is_accepted():
    config = SentryAIConfig(
        target_url="http://localhost:8080",
        testing_scope="local-dvwa",
    )
    config.validate()


def test_external_target_is_rejected():
    config = SentryAIConfig(
        target_url="https://example.com",
        testing_scope="local-dvwa",
    )
    with pytest.raises(ValueError, match="local DVWA"):
        config.validate()


def test_invalid_scheme_is_rejected():
    config = SentryAIConfig(
        target_url="ftp://localhost",
        testing_scope="local-dvwa",
    )
    with pytest.raises(ValueError, match="HTTP or HTTPS"):
        config.validate()


def test_missing_hostname_is_rejected():
    config = SentryAIConfig(
        target_url="http://",
        testing_scope="local-dvwa",
    )
    with pytest.raises(ValueError, match="hostname"):
        config.validate()


def test_invalid_log_level_is_rejected():
    config = SentryAIConfig(
        target_url="http://localhost:8080",
        testing_scope="local-dvwa",
        log_level="VERBOSE",
    )
    with pytest.raises(ValueError, match="log level"):
        config.validate()


def test_unapproved_scope_is_rejected():
    config = SentryAIConfig(
        target_url="http://localhost:8080",
        testing_scope="external-network",
    )
    with pytest.raises(ValueError, match="local-dvwa"):
        config.validate()
