<template>
    <div class="container mt-3">
        <div class="row mb-3">
            <div class="col">
                <input type="text" v-model="searchTerm" class="form-control" placeholder="Search by title" @input="fetchMovies" />
            </div>
            <div class="col">
                <select v-model="selectedGenre" @change="fetchMovies" class="form-select">
                    <option value="">All Genres</option>
                    <option v-for="genre in genres" :key="genre" :value="genre">{{ genre }}</option>
                </select>
            </div>
            <div class="col">
                <select v-model="selectedCollection" @change="fetchMovies" class="form-select">
                    <option value="">All Collections</option>
                    <option v-for="collection in collections" :key="collection" :value="collection">{{ collection }}</option>
                </select>
            </div>
            <div class="col">
                <select v-model="sortField" @change="fetchMovies" class="form-select">
                    <option value="vote_average">Vote Average</option>
                    <option value="release_date">Release Date</option>
                    <option value="popularity">Popularity</option>
                    <option value="title">Title</option>
                </select>
            </div>
            <div class="col">
                <select v-model="sortOrder" @change="fetchMovies" class="form-select">
                    <option value="asc">Ascending</option>
                    <option value="desc">Descending</option>
                </select>
            </div>
            <div class="col-auto">
                <button @click="prevPage" :disabled="currentPage <= 1" class="btn btn-secondary">Previous</button>
                <span class="px-2">{{ currentPage }} of {{ totalPages }}</span>
                <button @click="nextPage" :disabled="currentPage >= totalPages" class="btn btn-secondary">Next</button>
            </div>
        </div>

        <div v-for="movie in movies" :key="movie.id" class="row border-bottom">
            <div class="col">
                <img :src="movie.poster" alt="Movie poster" class="img-fluid movie-poster" />
            </div>
            <div class="col-5">
                <h4>{{ movie.title }}</h4>
            </div>
            <div v-if="movie.genres" class="col">
                <p>{{ movie.release_date.split('-')[0] }}</p>
                <p><strong>Rating: </strong>{{ movie.vote_average }} ({{ movie.vote_count }} votes)</p>
                <div>
                    <span v-for="genre in movie.genres.split(',')" :key="genre" class="badge" :class="genreClass(genre.trim())">{{ genre.trim() }}</span>
                </div>
            </div>
            <div v-else class="col">
                <p>{{ movie.release_date.split('-')[0] }}</p>
                <div>
                    <span class="badge bg-secondary">No Genre</span>
                </div>
            </div>
            <div class="col">
                <a :href="`${frontendUrl}/movie/${movie.imdb_id}`" class="btn btn-primary" target="_blank">Details</a>
            </div>
        </div>

        <div class="text-center">
            <button @click="prevPage" :disabled="currentPage <= 1" class="btn btn-secondary">Previous</button>
            <span class="px-2">{{ currentPage }} of {{ totalPages }}</span>
            <button @click="nextPage" :disabled="currentPage >= totalPages" class="btn btn-secondary">Next</button>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import { config } from '@/config';

export default {
    name: 'MoviesPage',
    data() {
        return {
            movies: [],
            frontendUrl: config.frontendUrl,
            selectedMovie: {},
            genres: [],
            selectedGenre: '',
            collections: [],
            selectedCollection: '',
            searchTerm: '',
            currentPage: 1,
            totalPages: 0,
            pageSize: 100,
            sortField: 'vote_average',
            sortOrder: 'desc',
        };
    },

    mounted() {
        this.fetchGenres();
        this.fetchCollections();
        this.fetchMovies();
        this.$nextTick(() => {
            this.initModal();
        });
    },
    methods: {
        genreClass(genre) {
            return `badge-${genre.toLowerCase().replace(/[\s&]+/g, '-')}`;
        },
        fetchGenres() {
            axios.get(`${config.backendUrl}/get_genres`).then((response) => {
                this.genres = response.data;
            });
        },
        fetchCollections() {
            axios.get(`${config.backendUrl}/get_collections`).then((response) => {
                this.collections = response.data.collections;
            });
        },
        fetchMovies() {
            const params = {
                page: this.currentPage,
                genre: this.selectedGenre,
                search: this.searchTerm.trim(),
                sort_by: this.sortField,
                order: this.sortOrder,
                collection: this.selectedCollection,
            };
            axios.get(`${config.backendUrl}/get_movies`, { params }).then((response) => {
                this.movies = response.data.movies;
                this.totalPages = Math.ceil(response.data.total / this.pageSize);
                this.movies.forEach((movie) => {
                    this.fetchPoster(movie);
                });
            });
        },

        initModal() {
            const modalElement = this.$refs.movieModal;
            if (modalElement) {
                this.myModal = new window.bootstrap.Modal(modalElement);
            }
        },
        fetchPoster(movie) {
            axios.get(`${config.backendUrl}/get_poster/${movie.imdb_id}`).then((response) => {
                movie.poster = response.data.poster_url;
            });
        },
        addToBacklog() {
            const payload = {
                username: localStorage.getItem('username'),
                movie_id: this.selectedMovie.id,
            };
            axios.post(`${config.backendUrl}/add_to_backlog`, payload).then(() => {
                alert('Movie added to your backlog successfully!');
            });
        },
        markAsWatched() {
            const movieId = this.selectedMovie.id;
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
                    if (this.movieModal) {
                        this.movieModal.hide();
                    }
                });
        },
        nextPage() {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                this.fetchMovies();
            }
        },
        prevPage() {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.fetchMovies();
            }
        },
    },
};
</script>
