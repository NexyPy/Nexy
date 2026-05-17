from nexy.compiler.parser.template import TemplateParser

parser = TemplateParser()

# Test case for nested HTML tags and components
html = """
<aside class="sidebar">
    <nav>
        <Link href="/home">Home</Link>
        <Link href="/about">About</Link>
    </nav>
    <div class="footer">
        <p>Footer content</p>
    </div>
</aside>
"""

known = {"Link"}

print("--- TESTING NESTED HTML TAGS (aside, nav, div) ---")
try:
    result = parser.parse(html, known_components=known)
    print("\n--- RESULT ---")
    print(result.strip())
    
    # Check if aside contains its children
    assert '<aside class="sidebar">' in result
    assert '</aside>' in result
    
    # Check if nav is inside aside
    # Check if Link is inside nav
    # Check if div is inside aside
    
    # A common issue with HTMLParser is that it might not handle some structures 
    # if it's not configured correctly or if the HTML is slightly malformed in its eyes.

except Exception as e:
    print(f"\n❌ FAILED")
    print(f"Error: {e}")
    if 'result' in locals():
        print(f"Generated: {result}")
