import { writable } from 'svelte/store';

interface User {
    name: string;
    profilePicture: string;
    role: string | null;
    user_id: number | null;
    loading: boolean;
}

export const userStore = writable<User>({
    name: '',
    profilePicture: '/default-avatar.png',
    role: '',
    user_id: null,
    loading: true
});

export const sidebarOpen = writable(true);