import { writable } from 'svelte/store';

interface User {
    name: string;
    profilePicture: string;
    role: string | null;
    loading: boolean;
}

export const userStore = writable<User>({
    name: '',
    profilePicture: '/default-avatar.png',
    role: '',
    loading: true
});

export const sidebarOpen = writable(true);