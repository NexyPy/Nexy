import pytest
from nexy.compiler.parser.template import TemplateParser, NexyParserError

class TestASTTemplateParser:
    def test_simple_component(self):
        parser = TemplateParser()
        result = parser.parse('<Button />', known_components={"Button"})
        assert result == '{{ Button() }}'

    def test_component_with_attributes(self):
        parser = TemplateParser()
        result = parser.parse('<Button title="Hello" count=5 />', known_components={"Button"})
        assert 'Button(title="Hello", count=5)' in result

    def test_nested_components(self):
        parser = TemplateParser()
        html = """
        <Grid>
            <Card title="Card 1">
                <Icon name="star" />
            </Card>
        </Grid>
        """
        known = {"Grid", "Card", "Icon"}
        result = parser.parse(html, known_components=known)
        
        assert '{% call Grid() %}' in result
        assert '{% call Card(title="Card 1") %}' in result
        assert '{{ Icon(name="star") }}' in result
        assert '{% endcall %}' in result

    def test_mixed_html_and_components(self):
        parser = TemplateParser()
        html = '<div class="container"><Button /><span>Text</span></div>'
        result = parser.parse(html, known_components={"Button"})
        assert '<div class="container">' in result
        assert '{{ Button() }}' in result
        assert '<span>Text</span>' in result

    def test_missing_import_raises_error(self):
        parser = TemplateParser()
        with pytest.raises(NexyParserError, match="Missing Import: <UnknownComponent>"):
            parser.parse('<UnknownComponent />')

    def test_self_closing_html_tags(self):
        parser = TemplateParser()
        html = '<img src="logo.png" /><br>'
        result = parser.parse(html)
        assert '<img src="logo.png" />' in result
        assert '<br />' in result or '<br>' in result # HTMLParser might normalize <br> to <br /> if we set it

    def test_dynamic_attributes(self):
        parser = TemplateParser()
        html = '<a href="/user/{{ id }}">Profile</a>'
        result = parser.parse(html)
        # Standard HTML tags attributes are not formatted by TemplateFormatter.format_dict in my current implementation
        # Wait, I should check if I want to support dynamic attributes in standard HTML tags too.
        # Nexy usually uses Jinja2 for that anyway: <a href="/user/{{ id }}">
        # The AST parser will just treat `{{ id }}` as part of the attribute value string.
        assert 'href="/user/{{ id }}"' in result

    def test_component_dynamic_attributes(self):
        parser = TemplateParser()
        html = '<Button link="/user/{{ id }}" />'
        result = parser.parse(html, known_components={"Button"})
        # Should be: {{ Button(link="/user/" ~ (id) ~ "") }}
        assert 'link="/user/" ~ (id)' in result
