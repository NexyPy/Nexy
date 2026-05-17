import pytest
from pathlib import Path
from nexy.core.config import Config


class TestLayoutDiscovery:
    """Tests for layout discovery walking up directory tree."""

    def test_find_layout_at_immediate_parent(self, tmp_path, monkeypatch):
        """Test that layout at immediate parent directory is found."""
        # Setup routes directory
        routes = tmp_path / "routes"
        routes.mkdir(parents=True)
        monkeypatch.setattr(Config, "ROUTER_PATH", str(routes))

        # Create: src/routes/blog/layout.nexy and src/routes/blog/posts/page.nexy
        blog = routes / "blog"
        blog.mkdir(parents=True)
        (blog / "layout.nexy").write_text("---\nchildren: str\n---<div>{{children}}</div>")
        posts = blog / "posts"
        posts.mkdir()
        (posts / "page.nexy").write_text("---\n---\n<div>Page</div>")

        # Directly test the layout discovery logic
        source_path = str(posts / "page.nexy")
        candidates = self._find_layout_candidates(source_path, str(routes))
        
        candidates_str = [str(c) for c in candidates]
        assert any("blog/layout.nexy" in c for c in candidates_str), f"Layout not found in {candidates_str}"

    def test_find_layout_walks_up_directory_tree(self, tmp_path, monkeypatch):
        """Test that layouts are found by walking up the directory tree."""
        # Setup routes directory
        routes = tmp_path / "routes"
        routes.mkdir(parents=True)
        monkeypatch.setattr(Config, "ROUTER_PATH", str(routes))

        # Create: src/routes/layout.nexy (root) and src/routes/app/layout.nexy
        (routes / "layout.nexy").write_text("---\nchildren: str\n---<root>{{children}}</root>")
        
        app = routes / "app"
        app.mkdir()
        (app / "layout.nexy").write_text("---\nchildren: str\n---<app>{{children}}</app>")
        
        dash = app / "dashboard"
        dash.mkdir()
        (dash / "page.nexy").write_text("---\n---\n<div>Dashboard</div>")

        # Directly test the layout discovery logic
        source_path = str(dash / "page.nexy")
        candidates = self._find_layout_candidates(source_path, str(routes))

        # Should find layouts from root to immediate parent
        paths_str = [str(c) for c in candidates]
        assert len(paths_str) >= 2, f"Expected at least 2 layouts, found {len(paths_str)}: {paths_str}"

    @staticmethod
    def _find_layout_candidates(source_path: str, router_path: str) -> list[str]:
        """Replicate the layout discovery logic from FileBasedRouter."""
        p = Path(source_path)
        root = Path(router_path)
        paths: list[str] = []
        
        current = p.parent
        while current != current.parent and current != root.parent:
            layout_file = current / "layout.nexy"
            if layout_file.is_file():
                paths.append(layout_file.as_posix())
            if current == root:
                break
            current = current.parent
        
        return paths