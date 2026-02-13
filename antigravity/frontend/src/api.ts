import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:5556', // Backend URL
});

export const crawlSite = async (url: string, recursive: boolean, max_pages: number = 10, enhance: boolean = false) => {
    const response = await api.post('/crawl', { url, recursive, max_pages, enhance });
    return response.data;
};

export const processContent = async (content_id: string, provider: string, model: string, instruction: string) => {
    const response = await api.post('/process', { content_id, provider, model, instruction });
    return response.data;
};

export const getModels = async () => {
    const response = await api.get('/models');
    return response.data;
}

export const getDownloadUrl = (content_id: string, type: 'original' | 'processed' = 'processed') => {
    return `http://localhost:5556/download/${content_id}?type=${type}`;
}
