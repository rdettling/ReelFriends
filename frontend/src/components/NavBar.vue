<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <img src="/logo.png" alt="ReelFriends Logo" height="30" class="d-inline-block align-top" />
                ReelFriends
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <router-link class="nav-link" to="/movies" active-class="active">Movies</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/backlog" active-class="active">Backlog</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/friends" active-class="active">Friends</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/profile" active-class="active">Profile</router-link>
                    </li>
                </ul>
                <span class="navbar-text text-light">
                    Signed in as {{ username }}
                    <router-link class="btn ms-2" to="/" @click="logout" :class="hoverClass" @mouseover="hover = true" @mouseout="hover = false">Sign out</router-link>
                </span>
            </div>
        </div>
    </nav>
</template>

<script>
import axios from 'axios';
import { config } from '@/config';

export default {
    data() {
        return {
            hover: false,
        };
    },
    computed: {
        username() {
            return localStorage.getItem('username');
        },
        hoverClass() {
            return {
                'btn-outline-light': !this.hover,
                'btn-success': this.hover,
            };
        },
    },
    methods: {
        logout() {
            axios.post(`${config.backendUrl}/logout`, {}).then(() => {
                localStorage.removeItem('username');
                this.$router.push('/');
            });
        },
    },
};
</script>
