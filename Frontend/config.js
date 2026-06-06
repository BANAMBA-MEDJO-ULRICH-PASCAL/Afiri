const API_BASE_URL = (() => {
    const host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1") {
        return "http://localhost:8000";
    }
    return window.AFIRI_API_URL || "https://afiri-api.onrender.com";
})();

const PROTECTED_PAGES = [
    "app.html",
    "offres.html",
    "profil.html",
    "quizz.html",
    "questionnaire.html",
    "detail-offre.html",
];
