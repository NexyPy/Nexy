from nexy.core.models import FFModel

source = """    import { h, render } from 'preact';
    import App from '@/App.svelte';

""" 
def preact()->FFModel:
    return FFModel(
        name="preact",
        render=source,
        extension=["jsx", "tsx"]
    )