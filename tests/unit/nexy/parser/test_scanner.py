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

def test_scanner_invalid_1():
    scanner = Scanner()
    with pytest.raises(ValueError):
        scanner.process(source_invalid_1)

source_invalid_2 = """
---
title = "Nexy"
show_hero = True

<div class="container">
    <h1>{{ title }}</h1>
</div>
"""

def test_scanner_invalid_2():
    scanner = Scanner()
    with pytest.raises(ValueError):
        scanner.process(source_invalid_2)


source_invalid_3 = """

title = "Nexy"
show_hero = True
----
<div class="container">
    <h1>{{ title }}</h1>
</div>
"""

def test_scanner_invalid_3():
    scanner = Scanner()
    with pytest.raises(ValueError):
        scanner.process(source_invalid_3)


source_invalid_4 = """
title = "Nexy"
show_hero = True
---
<h1>{{ title }}</h1>
---
"""


def test_scanner_invalid_4():
    scanner = Scanner()
    with pytest.raises(ValueError):
        scanner.process(source_invalid_4)

