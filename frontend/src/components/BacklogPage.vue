<template>
    <ul class="list-group">
        <li v-for="movie in movies" :key="movie.id" class="list-group-item">
            <div class="row">
                <div class="col text-center">
                    <img :src="movie.poster" alt="Movie poster" class="img-fluid" v-if="movie.poster" style="height: 100px" />
                </div>
                <div class="col">
                    <h4>{{ movie.title }}</h4>
                </div>
                <div class="col">
                    <div>{{ new Date(movie.release_date).getFullYear() }}</div>
                    <div>
                        <span v-for="genre in movie.genres.split(',')" :key="genre" class="badge me-1" :class="genreClass(genre.trim())">{{ genre.trim() }}</span>
                    </div>
                </div>
                <div class="col">
                    <strong>Added on:</strong>
                    <div>{{ formatDate(movie.added_on) }}</div>
                </div>
                <div class="col-3">
                    <a :href="`${frontendUrl}/movie/${movie.imdb_id}`" class="btn btn-primary mr-1" target="_blank">Details</a>
                    <button class="btn btn-success mr-1" @click.stop="markAsWatched(movie.id)">Mark as Watched</button>
                    <button class="btn btn-danger" @click.stop="removeFromBacklog(movie.id)">X</button>
                </div>
            </div>
        </li>
    </ul>
</template>

<script>
import axios from 'axios';
import { config } from '@/config';

export default {
    name: 'BacklogPage',
    data() {
        return {
            movies: [],
            frontendUrl: config.frontendUrl,
        };
    },
    mounted() {
        this.fetchBacklog();
    },
    methods: {
        fetchBacklog() {
            const username = localStorage.getItem('username');
            axios.get(`${config.backendUrl}/get_backlog?username=${username}`).then((response) => {
                this.movies = response.data.movies;
                this.movies.forEach((movie) => {
                    this.fetchPoster(movie);
                });
            });
        },
        fetchPoster(movie) {
            axios.get(`${config.backendUrl}/get_poster/${movie.imdb_id}`).then((response) => {
                movie.poster = response.data.poster_url;
            });
        },
        markAsWatched(movieId) {
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
                    this.fetchBacklog();
                });
        },
        removeFromBacklog(movieId) {
            axios.delete(`${config.backendUrl}/remove_from_backlog/${movieId}`).then(() => {
                this.fetchBacklog();
            });
        },
        formatNumber(value) {
            if (value === undefined || isNaN(value)) {
                return 'Not available';
            }
            return value.toLocaleString();
        },
        genreClass(genre) {
            return `badge-${genre.toLowerCase().replace(/[\s&]+/g, '-')}`;
        },
        formatDate(dateStr) {
            if (!dateStr) {
                return 'No date provided';
            }
            const date = new Date(dateStr.replace(' ', 'T'));
            if (isNaN(date.getTime())) {
                return 'Invalid date';
            }
            return new Intl.DateTimeFormat('en-US', {
                month: 'long',
                day: '2-digit',
                year: 'numeric',
            }).format(date);
        },
    },
};
</script>
