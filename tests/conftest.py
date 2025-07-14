"""Pytest configuration and shared fixtures."""

import pygame
import pytest


@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize pygame once for all tests."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture(autouse=True)
def suppress_pygame_output(monkeypatch):
    """Suppress pygame community message."""
    monkeypatch.setenv("PYGAME_HIDE_SUPPORT_PROMPT", "1")


@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary directory for test data."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    return data_dir
