export const BASE_URL = 'http://localhost:8000/api/v1';

export async function apiFetch(endpoint: string, options: RequestInit = {}): Promise<Response> {
    const headers: Record<string, string> = {
        'Accept': 'application/json',
        ...((options.headers as Record<string, string>) || {})
    };

   
    if (!headers['Content-Type']) {
        if (options.body instanceof FormData) {
        } else if (options.body instanceof URLSearchParams) {
            headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8';
        } else {
            headers['Content-Type'] = 'application/json';
        }
    }

    const defaultOptions: RequestInit = {
        ...options,
        credentials: 'include',
        headers
    };

    return fetch(`${BASE_URL}${endpoint}`, defaultOptions);
} 