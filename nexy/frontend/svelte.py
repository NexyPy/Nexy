from nexy.core.models import FFModel


source = """    import App from '@/App.svelte';

"""
def svelte()->FFModel:
    return FFModel(
        name="svelte",
        render=source,
        extension=["svelte"]
        )