from html.parser import HTMLParser

class TestParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print(f"START TAG: {tag}")
    def handle_data(self, data):
        print(f"DATA: {data}")

html = """
<a 
    href="{{ href }}" 
    {% if target %} target="{{ target }}" {% endif %}
>
    <span>Content</span>
</a>
"""

parser = TestParser()
parser.feed(html)
