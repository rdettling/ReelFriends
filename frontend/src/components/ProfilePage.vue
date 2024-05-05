<template>
    <div class="container mt-3">
        <div class="row">
            <div class="col-4">
                <h1>{{ username }}'s Profile</h1>
                <p><strong>Bio:</strong> {{ userProfile.bio }}</p>
                <button v-if="!editMode" @click="editMode = true" class="btn btn-outline-secondary">Edit Bio</button>
                <div v-if="editMode">
                    <textarea v-model="userProfile.bio" rows="3" class="form-control"></textarea>
                    <button @click="updateBio" class="btn btn-primary">Save Bio</button>
                    <button @click="editMode = false" class="btn btn-secondary">Cancel</button>
                </div>
                <h2>Friends</h2>
                <ul class="list-group">
                    <li v-for="friend in friends" :key="friend.username" class="list-group-item d-flex justify-content-between align-items-center">
                        <router-link :to="`/user/${friend.username}`">
                            {{ friend.username }}
                        </router-link>
                        <span class="badge bg-success">Friend</span>
                    </li>
                </ul>
            </div>
            <div class="col-8">
                <h1>Watched Movies</h1>
                <div v-for="movie in watchedMovies" :key="movie.id" class="row border-bottom" @click="selectMovie(movie)" style="cursor: pointer">
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

    <div class="modal fade" :class="{ show: isModalVisible }" tabindex="-1" role="dialog" :style="{ display: isModalVisible ? 'block' : 'none' }" @click.self="closeModal()">
        <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content" v-if="selectedMovie">
                <div class="modal-header">
                    <h5 class="modal-title">{{ selectedMovie.title }}</h5>
                </div>
                <div class="modal-body">
                    <div class="container-fluid">
                        <div class="row">
                            <div class="col-md-4">
                                <img :src="selectedMovie.poster" alt="Poster" class="img-fluid" />
                            </div>
                            <div class="col-md-8">
                                <p>
                                    <strong>Rating:</strong>
                                    <select v-model="selectedMovie.userRating" class="form-control">
                                        <option disabled value="">Select a rating</option>
                                        <option v-for="num in 10" :key="num" :value="num">{{ num }}</option>
                                    </select>
                                    <span> / 10</span>
                                    <br />
                                    <small>Current Rating: {{ selectedMovie.rating }}</small>
                                </p>
                                <p>
                                    <strong>Review:</strong>
                                    <textarea v-model="selectedMovie.userReview" rows="3" class="form-control"></textarea>
                                    <br />
                                    <small>Current Review: {{ selectedMovie.review }}</small>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="modal-footer">
                    <a :href="`${frontendUrl}/movie/${selectedMovie.imdb_id}`" class="btn btn-primary" target="_blank">Details</a>
                    <button type="button" class="btn btn-primary" @click="saveMovieReview(selectedMovie)">Save Changes</button>
                    <button type="button" class="btn btn-secondary" @click="closeModal()">Close</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import { config } from '@/config';

export default {
    name: 'ProfilePage',
    data() {
        return {
            username: '',
            userProfile: {},
            watchedMovies: [],
            frontendUrl: config.frontendUrl,
            editMode: false,
            selectedMovie: null,
            isModalVisible: false,
            friends: [],
        };
    },
    created() {
        this.username = localStorage.getItem('username');
        this.fetchUserProfile(this.username);
        this.fetchFriends(this.username);
        this.fetchWatchedMovies(this.username);
    },
    methods: {
        fetchUserProfile(username) {
            axios.get(`${config.backendUrl}/get_user_profile?username=${username}`).then((response) => {
                this.userProfile = response.data;
            });
        },
        fetchWatchedMovies(username) {
            axios.get(`${config.backendUrl}/get_watched_movies?username=${username}`).then((response) => {
                const movies = response.data.movies;
                const fetchPosterPromises = movies.map((movie) => fetchPoster(movie));
                Promise.all(fetchPosterPromises).then((updatedMovies) => {
                    this.watchedMovies = updatedMovies;
                });
            });
        },
        genreClass(genre) {
            return `badge-${genre.toLowerCase().replace(/[\s&]+/g, '-')}`;
        },
        updateBio() {
            const username = localStorage.getItem('username');
            axios.post(`${config.backendUrl}/update_bio`, { username: username, bio: this.userProfile.bio }).then(() => {
                this.editMode = false;
            });
        },
        selectMovie(movie) {
            this.selectedMovie = movie;
            this.isModalVisible = true;
        },

        closeModal() {
            this.isModalVisible = false;
            this.selectedMovie = null;
        },
        saveMovieReview(movie) {
            const data = {
                username: this.username,
                movie_id: movie.id,
                review: movie.userReview || '',
                rating: movie.userRating || null,
            };

            axios.post(`${config.backendUrl}/update_movie_review`, data).then(() => {
                this.isModalVisible = false;
                this.fetchWatchedMovies(this.username);
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
        fetchFriends(username) {
            axios.get(`${config.backendUrl}/friends/${username}`).then((response) => {
                this.friends = response.data.friends;
            });
        },
    },
};

function fetchPoster(movie) {
    return axios.get(`${config.backendUrl}/get_poster/${movie.imdb_id}`).then((response) => {
        movie.poster = response.data.poster_url;
        return movie;
    });
}
</script>

<style>
.modal.show {
    display: block;
}
.modal {
    overflow: auto;
}
</style>
