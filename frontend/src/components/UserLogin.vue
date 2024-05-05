<template>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow">
                    <div class="card-body">
                        <div class="text-center mb-4">
                            <img src="/logo.png" alt="ReelFriends Logo" class="mb-3" style="width: 120px" />
                            <h1 class="h3 mb-3 font-weight-normal">{{ isLoginMode ? 'Login to ReelFriends' : 'Create Your ReelFriends Account' }}</h1>
                            <p class="text-muted">A social movie sharing platform</p>
                        </div>
                        <form @submit.prevent="isLoginMode ? loginUser() : createUser()" class="p-4">
                            <div class="mb-3">
                                <label for="username" class="form-label">Username:</label>
                                <input type="text" class="form-control" id="username" v-model="credentials.username" required />
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Password:</label>
                                <input type="password" class="form-control" id="password" v-model="credentials.password" required />
                            </div>
                            <div v-if="!isLoginMode" class="mb-3">
                                <label for="confirmPassword" class="form-label">Confirm Password:</label>
                                <input type="password" class="form-control" id="confirmPassword" v-model="credentials.confirmPassword" required />
                            </div>
                            <button type="submit" class="btn btn-primary w-100">{{ isLoginMode ? 'Login' : 'Create Account' }}</button>
                        </form>
                        <div class="text-center">
                            <button @click="toggleMode" class="btn btn-link">{{ isLoginMode ? 'Need to create an account?' : 'Already have an account?' }}</button>
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
    data() {
        return {
            isLoginMode: true,
            credentials: {
                username: '',
                password: '',
                confirmPassword: '', // Only used for registration
            },
        };
    },
    methods: {
        loginUser() {
            axios
                .post(`${config.backendUrl}/login`, this.credentials, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })
                .then((response) => {
                    localStorage.setItem('username', response.data.username);
                    this.$router.push('/movies');
                })
                .catch((error) => {
                    if (error.response) {
                        // The request was made and the server responded with a status code
                        // that falls out of the range of 2xx
                        console.error('Server responded with error status:', error.response.status);
                        console.error('Error response data:', error.response.data);
                        // Handle specific error statuses (e.g., 401 for unauthorized)
                        if (error.response.status === 401) {
                            alert('Invalid username or password');
                        } else {
                            alert('An unexpected error occurred. Please try again later.');
                        }
                    } else if (error.request) {
                        // The request was made but no response was received
                        console.error('No response received from server');
                        alert('No response received from server. Please check your internet connection.');
                    } else {
                        // Something happened in setting up the request that triggered an error
                        console.error('Error setting up the request:', error.message);
                        alert('Error setting up the request. Please try again later.');
                    }
                });
        },

        createUser() {
            if (this.credentials.password !== this.credentials.confirmPassword) {
                alert('Passwords do not match!');
                return;
            }
            axios
                .post(`${config.backendUrl}/signup`, this.credentials, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })
                .then((response) => {
                    localStorage.setItem('username', response.data.username);
                    this.$router.push('/movies');
                })
                .catch((error) => {
                    if (error.response) {
                        // The request was made and the server responded with a status code
                        // that falls out of the range of 2xx
                        console.error('Server responded with error status:', error.response.status);
                        console.error('Error response data:', error.response.data);
                        // Handle specific error statuses (e.g., 401 for unauthorized)
                        if (error.response.status === 401) {
                            alert('Invalid username or password');
                        } else {
                            alert('An unexpected error occurred. Please try again later.');
                        }
                    } else if (error.request) {
                        // The request was made but no response was received
                        console.error('No response received from server');
                        alert('No response received from server. Please check your internet connection.');
                    } else {
                        // Something happened in setting up the request that triggered an error
                        console.error('Error setting up the request:', error.message);
                        alert('Error setting up the request. Please try again later.');
                    }
                });
        },

        toggleMode() {
            this.isLoginMode = !this.isLoginMode;
        },
    },
};
</script>
