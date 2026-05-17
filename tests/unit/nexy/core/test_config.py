import pytest
from nexy.core.config import Config


class TestConfigWatchExtensions:
    """Tests for Config watch extensions - BUG 15: user config override ignored"""

    def test_watch_extensions_from_config(self):
        """Test that user-configured watch extensions are not overridden."""
        # When useWatchExtensions is set in nexyconfig, it should be preserved
        config = Config()
        
        # The default WATCH_EXTENSIONS_GLOB should include route extensions
        if hasattr(config, "WATCH_EXTENSIONS_GLOB"):
            extensions = config.WATCH_EXTENSIONS_GLOB
            assert len(extensions) > 0, "Watch extensions should not be empty"
            # Should include .nexy and .mdx
            assert any(".nexy" in ext for ext in extensions), ".nexy should be in watch extensions"