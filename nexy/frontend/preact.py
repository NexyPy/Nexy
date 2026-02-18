def preact():
    return """
    import { h, render } from 'preact';
    import App from '@/App.svelte';
    render(<App />, document.body);
    """