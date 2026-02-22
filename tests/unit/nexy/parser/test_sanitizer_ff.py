from nexy.compiler.parser.sanitizer import LogicSanitizer

def test_tsx_maps_to_react():
    src = 'from "src/components/Button.tsx" import Button as Btn'
    out = LogicSanitizer().sanitize(src, current_file="src/routes/index.nexy")
    assert 'framework="react"' in out
    assert 'path="src/components/Button.tsx"' in out
    assert 'symbol="Button"' in out

def test_svelte_maps_to_svelte():
    src = 'from "src/components/Chip.svelte" import Chip'
    out = LogicSanitizer().sanitize(src, current_file="src/routes/index.nexy")
    assert 'framework="svelte"' in out
    assert 'path="src/components/Chip.svelte"' in out
    assert 'symbol="Chip"' in out
