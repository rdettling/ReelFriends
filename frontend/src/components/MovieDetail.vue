<template>
    <div class="container mt-3 movie-detail-page text-center" v-if="movie">
        <div class="row">
            <div class="col-3"></div>
            <div class="col-6">
                <h1>{{ movie.title }}</h1>
            </div>
            <div class="col">
                <button @click="addToBacklog" class="btn btn-primary me-2">Add to Backlog</button>
            </div>
            <div class="col">
                <button @click="markAsWatched" class="btn btn-success">Mark as Watched</button>
            </div>
        </div>
        <div class="row">
            <div class="col-md-4">
                <img :src="movie.poster" alt="Movie poster" class="img-fluid rounded" />
            </div>

            <div class="col-md-4">
                <div>
                    <span v-for="genre in movie.genres.split(',')" :key="genre" class="badge" :class="genreClass(genre.trim())">
                        {{ genre.trim() }}
                    </span>
                </div>
                <p><strong>Overview:</strong> {{ movie.overview }}</p>
                <p><strong>Language:</strong> {{ movie.original_language }}</p>
                <p><strong>Release Date:</strong> {{ movie.release_date }}</p>
                <p><strong>Runtime:</strong> {{ movie.runtime }} minutes</p>
                <p><strong>Budget:</strong> ${{ movie.budget.toLocaleString() }}</p>
                <p><strong>Revenue:</strong> ${{ movie.revenue.toLocaleString() }}</p>
                <p><strong>Production Companies:</strong> {{ movie.production_companies }}</p>
                <p><strong>Production Countries:</strong> {{ movie.production_countries }}</p>
                <p>
                    <strong>IMDb link:</strong> <a :href="'https://www.imdb.com/title/' + movie.imdb_id" target="_blank">{{ movie.imdb_id }}</a>
                </p>
                <p><strong>Popularity:</strong> {{ movie.popularity }}</p>
                <p><strong>Vote Average:</strong> {{ movie.vote_average }}/10</p>
                <p><strong>Vote Count:</strong> {{ movie.vote_count }}</p>
                <div class="mt-3"></div>
            </div>

            <div class="col-md-4">
                <h2 class="mb-3">Reviews & Ratings</h2>
                <div v-if="reviews.length">
                    <div v-for="review in reviews" :key="review.timestamp" class="card mb-3">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <router-link :to="{ name: 'User', params: { username: review.username } }" class="text-decoration-none">
                                {{ review.username }}
                            </router-link>
                            <small class="text-muted">
                                {{ new Date(review.timestamp).toLocaleDateString() }}
                            </small>
                        </div>
                        <div class="card-body">
                            <h5 class="card-title">Rating: {{ review.rating }}/10</h5>
                            <p class="card-text">{{ review.review }}</p>
                        </div>
                    </div>
                </div>
                <div v-else>
                    <p>No reviews yet.</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import { config } from '@/config';

export default {
    name: 'MovieDetail',
    props: {
        imdb_id: String,
    },
    data() {
        return {
            movie: null,
            reviews: [],
        };
    },
    created() {
        this.fetchMovieData();
    },

    methods: {
        fetchMovieData(imdb_id = this.imdb_id) {
            axios.get(`${config.backendUrl}/movies/${imdb_id}`).then((response) => {
                this.movie = response.data;
                this.fetchPoster(this.movie);
                this.fetchReviews(this.movie.id);
            });
        },
        fetchPoster(movie) {
            axios.get(`${config.backendUrl}/get_poster/${movie.imdb_id}`).then((response) => {
                this.movie.poster = response.data.poster_url;
            });
        },
        fetchReviews(movie_id) {
            axios.get(`${config.backendUrl}/reviews/${movie_id}`).then((response) => {
                this.reviews = response.data;
            });
        },
        addToBacklog() {
            const payload = {
                username: localStorage.getItem('username'),
                movie_id: this.movie.id,
            };
            axios.post(`${config.backendUrl}/add_to_backlog`, payload).then((response) => {
                alert(response.data.message || response.data.error);
            });
        },
        markAsWatched() {
            const movieId = this.movie.id;
            const username = localStorage.getItem('username');
            const review = prompt('Enter your review (optional):', '');
            const rating = prompt('Enter your rating (0-10, optional):', '');

            if (rating && (rating < 0 || rating > 10 || isNaN(rating))) {
                alert('Rating must be a number between 0 and 10.');
                return;
            }
            axios
                .post(`${config.backendUrl}/mark_watched`, {
                    username,
                    movie_id: movieId,
                    review: review || null,
                    rating: rating ? parseInt(rating) : null,
                })
                .then(() => {
                    alert('Movie marked as watched');
                    this.fetchReviews(movieId);
                });
        },
        genreClass(genre) {
            return `badge-${genre.toLowerCase().replace(/[\s&]+/g, '-')}`;
        },
    },
};
</script>
