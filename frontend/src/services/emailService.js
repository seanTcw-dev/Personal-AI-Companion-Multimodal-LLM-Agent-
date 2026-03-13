
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchEmails(limit = 20) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/emails?limit=${limit}`);
        if (!response.ok) throw new Error('Failed to fetch emails');
        return await response.json();
    } catch (error) {
        console.error('Error fetching emails:', error);
        return { emails: [], unread_count: 0 };
    }
}

export async function refreshEmails() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/emails/refresh`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to refresh emails');
        return await response.json();
    } catch (error) {
        console.error('Error refreshing emails:', error);
        return null;
    }
}

export async function fetchNews(limit = 5) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/news?limit=${limit}`);
        if (!response.ok) throw new Error('Failed to fetch news');
        return await response.json();
    } catch (error) {
        console.error('Error fetching news:', error);
        return { news: [] };
    }
}

export async function refreshNews(limit = 5) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/news/refresh?limit=${limit}`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to refresh news');
        return await response.json();
    } catch (error) {
        console.error('Error refreshing news:', error);
        return null;
    }
}

export async function generateEmail() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/emails/generate`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to generate email');
        return await response.json();
    } catch (error) {
        console.error('Error generating email:', error);
        return null;
    }
}
