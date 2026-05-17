import pytest
from nexy.core.models import ScanResult
from nexy.compiler.parser.scanner import Scanner

source_valid = """
---
title = "Nexy"
show_hero = True
---
<div class="container">
    <h1>{{ title }}</h1>
</div>
"""


def test_scanner_valid():
    scanner = Scanner()
    result = scanner.process(source_valid)
    assert 'title = "Nexy"' in result.frontmatter 
    assert 'show_hero = True' in result.frontmatter 
    assert '<div class="container">' in result.template
    assert '<h1>{{ title }}</h1>' in result.template 
    assert '</div>' in result.template 

source_valid_1 = """
---
title = "Nexy"
show_hero = True
---
<h1>{{ title }}</h1>
---
<div class="container">
    <h1>{{ title }}</h1>
</div>
"""
def test_scanner_valid_1():
    scanner = Scanner()
    result = scanner.process(source_valid_1)
    assert 'title = "Nexy"' in result.frontmatter 
    assert 'show_hero = True' in result.frontmatter 
    assert '<h1>{{ title }}</h1>' in result.template
    assert '---' in result.template
    assert '<div class="container">' in result.template
    assert '</div>' in result.template
    assert '<h1>{{ title }}</h1>' in result.template


source_invalid_1 = """

title = "Nexy"
show_hero = True
<div class="container">
    <h1>{{ title }}</h1>
</div>
"""

def test_scanner_no_frontmatter():
    scanner = Scanner()
    result = scanner.process(source_invalid_1)
    assert result.frontmatter == ""
    assert '<div class="container">' in result.template

source_invalid_2 = """
---
title = "Nexy"
show_hero = True

<div class="container">
    <h1>{{ title }}</h1>
</div>
"""

def test_scanner_unclosed_frontmatter():
    scanner = Scanner()
    with pytest.raises(ValueError, match="Unclosed '---' delimiter"):
        scanner.process(source_invalid_2)


source_invalid_3 = """

title = "Nexy"
show_hero = True
----
<div class="container">
    <h1>{{ title }}</h1>
</div>
"""

def test_scanner_no_frontmatter_with_dashes():
    scanner = Scanner()
    result = scanner.process(source_invalid_3)
    assert result.frontmatter == ""
    assert "----" in result.template


source_invalid_4 = """
title = "Nexy"
show_hero = True
---
<h1>{{ title }}</h1>
---
"""


def test_scanner_frontmatter_not_at_start():
    scanner = Scanner()
    result = scanner.process(source_invalid_4)
    assert result.frontmatter == ""
    assert 'title = "Nexy"' in result.template

