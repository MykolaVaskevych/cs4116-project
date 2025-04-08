export const environment = {
    production: true,
    apiHost: (window as any)["env"]["apiHost"] || 'https://cs4116-project-production.up.railway.app',
    randomUserApi: 'https://randomuser.me'
};