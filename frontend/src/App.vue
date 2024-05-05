<template>
    <div id="app">
        <NavBar v-if="$route.name !== 'Login'" />
        <router-view />
    </div>
</template>

<script>
import NavBar from './components/NavBar.vue';

export default {
    name: 'App',
    components: {
        NavBar,
    },
};
</script>

<style>
.badge-comedy {
    background-color: #f0db4f; /* Light, cheerful yellow */
}
.badge-drama {
    background-color: #c0c0c0; /* Serious, neutral grey */
}
.badge-romance {
    background-color: #ff66b2; /* Romantic pink */
}
.badge-action {
    background-color: #c70039; /* Intense red */
}
.badge-horror {
    background-color: #880000; /* Dark red */
}
.badge-thriller {
    background-color: #333333; /* Mysterious dark grey */
}
.badge-science-fiction {
    background-color: #4d4dff; /* Futuristic blue */
}
.badge-fantasy {
    background-color: #7f00ff; /* Enchanting violet */
}
.badge-animation {
    background-color: #ff9933; /* Bright orange */
}
.badge-documentary {
    background-color: #008080; /* Earthy teal */
}
.badge-crime {
    background-color: #004d4d; /* Deep teal */
}
.badge-history {
    background-color: #cc8800; /* Historical gold */
}
.badge-war {
    background-color: #808000; /* Military olive */
}
.badge-family {
    background-color: #00cc99; /* Friendly aqua */
}
.badge-adventure {
    background-color: #007399; /* Bold blue */
}
.badge-foreign {
    background-color: #009999; /* Exotic cyan */
}
.badge-music {
    background-color: #cc00cc; /* Vibrant purple */
}
.badge-mystery {
    background-color: #3d405b; /* Mysterious indigo */
}
.badge-western {
    background-color: #8b4513; /* Saddle Brown */
}
.badge-tv-movie {
    background-color: #00f7ff;
}

.badge {
    margin: 2px;
}

.movie-poster {
    max-height: 100px;
    width: auto;
}
</style>
