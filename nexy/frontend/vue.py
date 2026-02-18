def vue():
    return """
    import Vue from 'vue';
    import App from '@/App.svelte';
    new Vue({
        render: h => h(App),
    }).$mount(document.body);
    """