const API_BASE_URL = (() => {
    if (window.AFIRI_API_URL) return window.AFIRI_API_URL;
    const stored = localStorage.getItem("afiri_api_url");
    if (stored) return stored;

    const host = window.location.hostname;
    const protocol = window.location.protocol;

    const isLocal =
        protocol === "file:" ||
        !host ||
        host === "localhost" ||
        host === "127.0.0.1" ||
        host.startsWith("192.168.") ||
        host.startsWith("10.");

    if (isLocal) return "http://127.0.0.1:8000";

    return "https://afiri-api.onrender.com";
})();

const PROTECTED_PAGES = [
    "app.html",
    "offres.html",
    "profil.html",
    "quizz.html",
    "questionnaire.html",
    "detail-offre.html",
];
