import { createRouter, createWebHistory } from 'vue-router';
import UserLogin from '../components/UserLogin.vue';
import MoviesPage from '../components/MoviesPage.vue';
import BacklogPage from '../components/BacklogPage.vue';
import FriendsPage from '../components/FriendsPage.vue';
import ProfilePage from '../components/ProfilePage.vue';
import UserPage from '../components/UserPage.vue';
import MovieDetail from '../components/MovieDetail.vue';

const routes = [
    {
        path: '/',
        name: 'Login',
        component: UserLogin,
        meta: {
            title: 'Login',
        },
    },
    {
        path: '/movies',
        name: 'Movies',
        component: MoviesPage,
        meta: {
            title: 'Movies',
        },
    },

    {
        path: '/backlog',
        name: 'Backlog',
        component: BacklogPage,
        meta: {
            title: 'Backlog',
        },
    },
    {
        path: '/friends',
        name: 'Friends',
        component: FriendsPage,
        meta: {
            title: 'Friends',
        },
    },
    {
        path: '/profile',
        name: 'Profile',
        component: ProfilePage,
        meta: {
            title: 'Profile',
        },
    },
    {
        path: '/user/:username',
        name: 'User',
        component: UserPage,
        props: true,
        meta: {
            title: 'User Profile',
        },
    },
    {
        path: '/movie/:imdb_id',
        name: 'MovieDetail',
        component: MovieDetail,
        props: true,
        meta: {
            title: 'Movie Detail',
        },
    },
];

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes,
});

export default router;
