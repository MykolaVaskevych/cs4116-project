// This file will be processed during build
// The window.ENV object will be injected by Nginx
declare global {
    interface Window {
        ENV?: {
            BACKEND_URL?: string;
        };
    }
}

export const environment = {
    production: true,
    apiHost: window.ENV?.BACKEND_URL || 'https://backend.railway.app',
    randomUserApi: 'https://randomuser.me'
};