<template>
    <div class="container mt-3">
        <div class="row">
            <div class="col-4">
                <h1>{{ username }}'s Profile</h1>
                <p><strong>Bio:</strong> {{ userProfile.bio }}</p>
                <h2>Friends</h2>
                <ul class="list-group">
                    <li v-for="friend in friends" :key="friend.username" class="list-group-item d-flex justify-content-between align-items-center">
                        <!-- Conditional routing based on whether the friend is the current user -->
                        <router-link :to="friend.username === currentUser ? '/profile' : `/user/${friend.username}`">
                            {{ friend.username }}
                        </router-link>
                        <span v-if="friend.username === currentUser" class="badge bg-primary">You</span>
                        <span v-else-if="friend.isFriend" class="badge bg-success">Friend</span>
                        <button v-else @click="addFriend(friend.username)" class="btn btn-sm btn-primary">Add Friend</button>
                    </li>
                </ul>
            </div>
            <div class="col-8">
                <h1>Watched Movies</h1>
                <div v-for="movie in watchedMovies" :key="movie.id" class="row border-bottom">
                    <div class="col-2">
                        <img :src="movie.poster" alt="Movie poster" class="img-fluid movie-poster" />
                    </div>
                    <div class="col">
                        <h5>{{ movie.title }}</h5>
                        <p>{{ movie.release_date.split('-')[0] }}</p>
                        <div>
                            <span v-for="genre in movie.genres.split(',')" :key="genre" class="badge" :class="genreClass(genre.trim())">{{ genre.trim() }}</span>
                        </div>
                    </div>
                    <div class="col-4 text-end">
                        <p class="m-0"><strong>Watched on: </strong>{{ formatTimestamp(movie.timestamp) }}</p>
                        <span v-if="movie.rating" class="badge bg-info">{{ movie.rating }}/10</span>
                        <span v-else class="badge bg-secondary">Unrated</span>
                        <p class="m-0"><strong>Review:</strong> {{ movie.review }}</p>
                        <a :href="`${frontendUrl}/movie/${movie.imdb_id}`" class="btn btn-primary mb-1" target="_blank">Details</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import { config } from '@/config';

export default {
    name: 'UserPage',
    props: {
        username: String,
    },
    data() {
        return {
            userProfile: {},
            watchedMovies: [],
            friends: [],
            currentUser: localStorage.getItem('username'),
        };
    },
    mounted() {
        this.fetchUserData(this.username);
        this.fetchUserMovies(this.username);
        this.fetchFriends(this.username);
    },

    watch: {
        '$route.params.username'(newUsername, oldUsername) {
            if (newUsername !== oldUsername) {
                this.fetchUserData(newUsername);
                this.fetchUserMovies(newUsername);
                this.fetchFriends(newUsername);
            }
        },
    },
    methods: {
        fetchUserData(username) {
            axios.get(`${config.backendUrl}/get_user_profile?username=${username}`).then((response) => {
                this.userProfile = response.data;
            });
        },
        fetchUserMovies(username) {
            axios.get(`${config.backendUrl}/get_watched_movies?username=${username}`).then((response) => {
                this.watchedMovies = response.data.movies;
                this.watchedMovies.forEach((movie) => {
                    this.fetchPoster(movie);
                });
            });
        },
        fetchPoster(movie) {
            axios.get(`${config.backendUrl}/get_poster/${movie.imdb_id}`).then((response) => {
                movie.poster = response.data.poster_url;
            });
        },
        fetchFriends(username) {
            axios.get(`${config.backendUrl}/friends/${username}`).then((response) => {
                this.friends = response.data.friends;
                this.checkFriendship();
            });
        },
        checkFriendship() {
            const currentUser = this.currentUser;
            axios.get(`${config.backendUrl}/friends/${currentUser}`).then((response) => {
                const currentUserFriends = response.data.friends.map((friend) => friend.username);
                this.friends = this.friends.map((friend) => {
                    return {
                        ...friend,
                        isFriend: currentUserFriends.includes(friend.username) || friend.username === currentUser,
                    };
                });
            });
        },
        formatTimestamp(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleDateString('en-US', {
                month: 'long',
                day: 'numeric',
                year: 'numeric',
            });
        },
        addFriend(friendUsername) {
            axios.post(`${config.backendUrl}/add_friend`, { user_a: this.currentUser, user_b: friendUsername }).then(() => {
                this.fetchFriends(this.username); // Refresh friends list
            });
        },
        genreClass(genre) {
            return `badge-${genre.toLowerCase().replace(/[\s&]+/g, '-')}`;
        },
    },
};
</script>
