import pytest
from nexy.cli.commands.utilities.watcher import WatchHandler


class TestWatchHandlerNormalize:
    """Tests for WatchHandler._normalize() method - BUG 1: str.decode() error"""

    def test_normalize_handles_string(self):
        """Test that _normalize handles str input without error."""
        handler = WatchHandler()
        result = handler._normalize("some/path/to/file.nexy")
        assert result == "some/path/to/file.nexy"

    def test_normalize_handles_bytes(self):
        """Test that _normalize handles bytes input without error."""
        handler = WatchHandler()
        result = handler._normalize(b"some/path/to/file.nexy")
        assert result == "some/path/to/file.nexy"

    def test_normalize_converts_backslashes(self):
        """Test that backslashes are converted to forward slashes."""
        handler = WatchHandler()
        result = handler._normalize("src\\routes\\index.nexy")
        assert result == "src/routes/index.nexy"

    def test_normalize_strips_dot_slash(self):
        """Test that leading ./ is stripped."""
        handler = WatchHandler()
        result = handler._normalize("./src/routes/index.nexy")
        assert result == "src/routes/index.nexy"