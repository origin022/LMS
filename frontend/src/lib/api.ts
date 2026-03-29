export const BASE_URL = 'http://localhost:8000/api/v1';

export async function apiFetch(endpoint: string, options: RequestInit = {}): Promise<Response> {
    const token = localStorage.getItem("token");

    const headers: Record<string, string> = {
        'Accept': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...((options.headers as Record<string, string>) || {})
    };

    if (!headers['Content-Type']) {
        if (options.body instanceof FormData) {
        } else if (options.body instanceof URLSearchParams) {
            headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8';
        } else if (options.body) {
            headers['Content-Type'] = 'application/json';
        }
    }

    return fetch(`${BASE_URL}/${endpoint.replace(/^\//, '')}`, {
        ...options,
        credentials: 'include',
        headers
    });
} 