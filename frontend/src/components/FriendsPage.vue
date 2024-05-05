<template>
    <div class="p-3">
        <div class="row">
            <div class="col-3">
                <h2>My Friends</h2>
                <div class="list-group">
                    <a v-for="friend in friends" :key="friend.username" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                        {{ friend.username }}
                        <router-link :to="`/user/${friend.username}`" class="badge badge-primary">View Profile</router-link>
                    </a>
                </div>
            </div>
            <div class="col-3">
                <h2>Add Friends</h2>
                <div class="list-group">
                    <div v-for="user in nonFriends" :key="user.username" class="list-group-item list-group-item-action">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">{{ user.username }}</h5>
                            <small>
                                <router-link :to="`/user/${user.username}`" class="badge badge-primary">View Profile</router-link>
                            </small>
                        </div>
                        <button @click="addFriend(user.username)" class="btn btn-sm btn-success mt-2">Add Friend</button>
                    </div>
                </div>
            </div>
            <div class="col-6">
                <h2>Friend Activity</h2>
                <div v-for="movie in friendActivities" :key="movie.id" class="mb-3">
                    <div class="row">
                        <div class="col">
                            <img :src="movie.poster" alt="Movie Poster" class="img-fluid mb-2 movie-poster" />
                        </div>
                        <div class="col">
                            <p class="m-0">
                                <strong>{{ movie.username }} watched:</strong> {{ movie.title }}
                                <span v-for="genre in movie.genres.split(',')" :key="genre" class="badge" :class="genreClass(genre.trim())">{{ genre.trim() }}</span>
                            </p>
                        </div>
                        <div class="col">
                            <p class="m-0"><strong>Watched on:</strong> {{ formatTimestamp(movie.timestamp) }}</p>
                        </div>
                        <div class="col">
                            <span v-if="movie.rating" class="badge bg-info">{{ movie.rating }}/10</span>
                            <span v-else class="badge bg-secondary">Unrated</span>
                            <p class="m-0"><strong>Review:</strong> {{ movie.review }}</p>
                        </div>
                        <div class="col">
                            <a :href="`${frontendUrl}/movie/${movie.imdb_id}`" class="btn btn-primary mb-1" target="_blank">Details</a>
                        </div>
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
    name: 'FriendsPage',
    data() {
        return {
            friends: [],
            nonFriends: [],
            friendActivities: [],
            frontendUrl: config.frontendUrl,
        };
    },
    mounted() {
        this.fetchFriends();
        this.fetchFriendActivities();
    },
    methods: {
        fetchFriends() {
            const currentUser = localStorage.getItem('username');
            axios.get(`${config.backendUrl}/friends/${currentUser}`).then((response) => {
                this.friends = response.data.friends;
                this.nonFriends = response.data.nonFriends;
            });
        },
        addFriend(username) {
            const currentUser = localStorage.getItem('username');
            axios.post(`${config.backendUrl}/add_friend`, { user_a: currentUser, user_b: username }).then(() => {
                this.fetchFriends();
                this.fetchFriendActivities();
            });
        },
        fetchFriendActivities() {
            const currentUser = localStorage.getItem('username');
            axios.get(`${config.backendUrl}/friend_activities/${currentUser}`).then((response) => {
                Promise.all(response.data.activities.map((movie) => this.fetchPoster(movie))).then((movies) => {
                    this.friendActivities = movies;
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
        genreClass(genre) {
            return `badge-${genre.toLowerCase().replace(/[\s&]+/g, '-')}`;
        },
        fetchPoster(movie) {
            return axios.get(`${config.backendUrl}/get_poster/${movie.imdb_id}`).then((response) => {
                movie.poster = response.data.poster_url;
                return movie;
            });
        },
    },
};
</script>
