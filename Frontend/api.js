/**
 * api.js — Couche de communication entre le front-end et l'API Afiri.
 * Importé par toutes les pages HTML via <script src="api.js"></script>
 * Gère : stockage du token JWT, appels fetch vers FastAPI, erreurs.
 */

// API_URL est défini dans config.js (chargé avant api.js dans chaque page HTML)

// ─────────────────────────────────────────────────────────────────
// AUTH — stockage et lecture du token JWT
// ─────────────────────────────────────────────────────────────────

const Auth = {
  save(token, role) {
    localStorage.setItem("afiri_token", token);
    localStorage.setItem("afiri_role", role);
  },
  getToken() { return localStorage.getItem("afiri_token"); },
  getRole()  { return localStorage.getItem("afiri_role"); },
  isLoggedIn() { return !!this.getToken(); },

  logout() {
    localStorage.removeItem("afiri_token");
    localStorage.removeItem("afiri_role");
    localStorage.removeItem("afiri_user");
    window.location.href = "signup.html";
  },

  /** Redirige vers signup si non connecté */
  requireAuth() {
    if (!this.isLoggedIn()) { window.location.href = "signup.html"; return false; }
    return true;
  },

  saveUser(u) { localStorage.setItem("afiri_user", JSON.stringify(u)); },
  getUser()   {
    const u = localStorage.getItem("afiri_user");
    return u ? JSON.parse(u) : null;
  }
};

// ─────────────────────────────────────────────────────────────────
// FETCH CENTRAL — ajoute automatiquement le token JWT
// ─────────────────────────────────────────────────────────────────

async function apiFetch(endpoint, options = {}, withAuth = true) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (withAuth && Auth.getToken()) {
    headers["Authorization"] = `Bearer ${Auth.getToken()}`;
  }

  const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });

  if (res.status === 401) { Auth.logout(); return null; }
  if (res.status === 204) return null;  // No Content

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Erreur inconnue" }));
    throw new Error(err.detail || `Erreur ${res.status}`);
  }
  return res.json();
}

// ─────────────────────────────────────────────────────────────────
// AUTHENTIFICATION
// ─────────────────────────────────────────────────────────────────

const ApiAuth = {
  /**
   * Connexion via OAuth2 (FastAPI attend du x-www-form-urlencoded).
   * Le champ s'appelle "username" mais on y met l'email — c'est le standard OAuth2.
   */
  async login(email, motDePasse) {
    const body = new URLSearchParams();
    body.append("username", email);
    body.append("password", motDePasse);

    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Erreur de connexion" }));
      throw new Error(err.detail || "Email ou mot de passe incorrect.");
    }

    const data = await res.json();
    // Décoder le rôle depuis le payload JWT (partie centrale en base64)
    const payload = JSON.parse(atob(data.access_token.split(".")[1]));
    Auth.save(data.access_token, payload.role);
    return data;
  },

  /** Inscription d'un nouveau compte */
  async register(email, motDePasse, role = "etudiant") {
    return apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, mot_de_passe: motDePasse, role }),
    }, false);
  },

  /** Récupère les infos de l'utilisateur connecté depuis /auth/me */
  async fetchMe() {
    const user = await apiFetch("/auth/me");
    if (user) Auth.saveUser(user);
    return user;
  }
};

// ─────────────────────────────────────────────────────────────────
// OFFRES
// ─────────────────────────────────────────────────────────────────

const ApiOffres = {
  async lister(search = "") {
    const q = search ? `?search=${encodeURIComponent(search)}` : "";
    return apiFetch(`/offres/${q}`, {}, false);
  },
  async detail(id) {
    return apiFetch(`/offres/${id}`, {}, false);
  }
};

// ─────────────────────────────────────────────────────────────────
// PROFIL ÉTUDIANT
// ─────────────────────────────────────────────────────────────────

const ApiProfil = {
  async moi()             { return apiFetch("/profils/moi"); },
  async creer(data)       { return apiFetch("/profils/", { method: "POST", body: JSON.stringify(data) }); },
  async mettreAJour(data) { return apiFetch("/profils/moi", { method: "PUT",  body: JSON.stringify(data) }); }
};

// ─────────────────────────────────────────────────────────────────
// CANDIDATURES
// ─────────────────────────────────────────────────────────────────

const ApiCandidatures = {
  async postuler(offreId, lettre = "") {
    return apiFetch("/candidatures/", {
      method: "POST",
      body: JSON.stringify({ offre_id: offreId, lettre_motivation: lettre }),
    });
  },
  async mesCandidatures() { return apiFetch("/candidatures/moi"); }
};

// ─────────────────────────────────────────────────────────────────
// QUIZ
// ─────────────────────────────────────────────────────────────────

const ApiQuiz = {
  async envoyer(reponses)  { return apiFetch("/quiz/envoyer", { method: "POST", body: JSON.stringify({ reponses }) }); },
  async monDernier()       { return apiFetch("/quiz/mon-dernier"); },
  async resultats(quizId)  { return apiFetch(`/quiz/resultats/${quizId}`); }
};

// ─────────────────────────────────────────────────────────────────
// UTILITAIRES UI
// ─────────────────────────────────────────────────────────────────

/** Affiche un message d'erreur dans un élément HTML pendant 5 s */
function afficherErreur(elementId, message) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.textContent = message;
  el.style.display = "block";
  setTimeout(() => { el.style.display = "none"; }, 5000);
}

/** Formate une date ISO en français : "15 mai 2024" */
function formaterDate(dateIso) {
  if (!dateIso) return "—";
  return new Date(dateIso).toLocaleDateString("fr-FR", {
    day: "numeric", month: "long", year: "numeric"
  });
}

/** Calcule le % de complétion d'un profil étudiant */
function calculerCompletionProfil(profil) {
  if (!profil) return 0;
  const champs = ["nom", "prenom", "formation", "universite", "competences", "experiences", "cv_lien"];
  const remplis = champs.filter(c => profil[c] && String(profil[c]).trim() !== "").length;
  return Math.round((remplis / champs.length) * 100);
}
