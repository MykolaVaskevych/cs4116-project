// Check if we're running on Railway
const isRailway = typeof window !== 'undefined' && window.location.hostname.includes('railway.app');

export const environment = {
    production: false,
    // Use Railway backend URL if running on Railway, otherwise localhost
    apiHost: isRailway
        ? 'https://cs4116-project-production.up.railway.app'
        : 'http://localhost:8000',
    randomUserApi: 'https://randomuser.me',
};
