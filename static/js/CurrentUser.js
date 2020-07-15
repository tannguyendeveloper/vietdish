export default class CurrentUser {
    static async redirectIfNotAuthenticated() {
        const isUserAuthenticated = await fetch('/authenticate');
        if(isUserAuthenticated.status !== 200) {
            window.location.href = "/login";
            return false
        }        
        return true
    }
}

