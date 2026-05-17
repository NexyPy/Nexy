from nexy.compiler.parser.template import TemplateParser

parser = TemplateParser()

# Test case with multiple nested tags and potential malformation
html = """
<header class="h-header">
    <menu class="m-menu">
        <nav class="n-nav">
            <Link href="/">
                <img src="logo.svg" />
            </Link>
            <ul class="u-list">
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </nav>
        <aside class="a-aside">
            <Search />
            <Link href="/btn">
                Click
                <svg>
                    <path d="M1 1" />
                </svg>
            </Link>
        </aside>
    </menu>
</header>
"""

known = {"Link", "Search", "Card"}

print("--- TESTING DEEP NESTING ---")
try:
    result = parser.parse(html, known_components=known)
    print("\n--- RESULT ---")
    print(result.strip())
    
    # Check if nested structure is preserved
    assert '<header' in result
    assert '<menu' in result
    assert '<nav' in result
    assert '<aside' in result
    
    # Check if Link contains children
    assert '{% call Link' in result
    assert '<img' in result
    assert '{% endcall %}' in result

except Exception as e:
    print(f"\n❌ FAILED")
    print(f"Error: {e}")
    if 'result' in locals():
        print(f"Generated: {result}")
