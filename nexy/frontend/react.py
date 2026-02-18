def react():
    return """
    import React from 'react';
    import ReactDOM from 'react-dom';
    import App from '@/App.svelte';
    ReactDOM.render(<App />, document.body);
    """