from nexy.compiler.parser.template import TemplateParser, TemplateFormatter


class TestTemplateFormatter:
    def test_format_attributes_no_spaces_around_equals(self):
        result = TemplateFormatter.format_attributes('foo="bar"')
        assert result == 'foo="bar"'

    def test_format_attributes_spaces_around_equals(self):
        result = TemplateFormatter.format_attributes('foo = "bar"')
        assert result == 'foo="bar"'

    def test_format_attributes_multiple_with_spaces(self):
        result = TemplateFormatter.format_attributes('foo = "bar" baz = "qux"')
        assert result == 'foo="bar", baz="qux"'

    def test_format_attributes_mixed_spaces(self):
        result = TemplateFormatter.format_attributes('foo="bar" baz = "qux"')
        assert result == 'foo="bar", baz="qux"'


class TestTemplateParser:
    def test_self_closing_without_spaces(self):
        parser = TemplateParser()
        result = parser.parse('<Button />', known_components={"Button"})
        assert "Button()" in result

    def test_self_closing_with_spaces_around_equals(self):
        parser = TemplateParser()
        result = parser.parse('<Button title = "Hello" />', known_components={"Button"})
        assert "Button(title=\"Hello\")" in result

    def test_self_closing_mixed_spaces(self):
        parser = TemplateParser()
        result = parser.parse('<Button title="Hello" count = 5 />', known_components={"Button"})
        assert "title=\"Hello\"" in result
        assert "count=5" in result
