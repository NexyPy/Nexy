# mdx page
bonjour! This is the about page of Nexy. 
Nexy is a static site generator that helps you build fast and modern websites with ease.
{{ name }}

{%for item in title %}
 1. {{ item }}

{% endfor %}


{% call User() %}
```python
 def user():
    print("user")

```
{% endcall %}
dhj