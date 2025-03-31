export const environment = {
    production: true,
    apiHost: (window as any)["env"]["apiHost"] || 'https://backend-production-5eff.up.railway.app',
    randomUserApi: 'https://randomuser.me'
};