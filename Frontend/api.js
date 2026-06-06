const TOKEN_KEY = "afiri_token";

const Auth = {
    getToken() {
        return localStorage.getItem(TOKEN_KEY);
    },
    setToken(token) {
        localStorage.setItem(TOKEN_KEY, token);
    },
    clearToken() {
        localStorage.removeItem(TOKEN_KEY);
    },
    isLoggedIn() {
        return !!this.getToken();
    },
    logout() {
        this.clearToken();
        window.location.href = "signup.html";
    },
};

async function apiFetch(path, options = {}) {
    const headers = { ...(options.headers || {}) };
    const token = Auth.getToken();
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }
    if (options.body && !(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

    if (response.status === 401) {
        Auth.clearToken();
        if (!window.location.pathname.endsWith("signup.html") && !window.location.pathname.endsWith("index.html")) {
            window.location.href = "signup.html";
        }
        throw new Error("Non authentifié");
    }

    if (!response.ok) {
        let detail = "Erreur serveur";
        try {
            const err = await response.json();
            detail = err.detail || detail;
        } catch (_) { /* ignore */ }
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }

    if (response.status === 204) return null;
    return response.json();
}

const ApiAuth = {
    async register({ email, mot_de_passe, nom, prenom, universite, role = "etudiant" }) {
        return apiFetch("/auth/register", {
            method: "POST",
            body: JSON.stringify({ email, mot_de_passe, nom, prenom, universite, role }),
        });
    },
    async login(email, password) {
        const form = new URLSearchParams();
        form.append("username", email);
        form.append("password", password);
        const data = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: form,
        }).then(async (r) => {
            if (!r.ok) {
                const err = await r.json().catch(() => ({}));
                throw new Error(err.detail || "Email ou mot de passe incorrect.");
            }
            return r.json();
        });
        Auth.setToken(data.access_token);
        return data;
    },
    async me() {
        return apiFetch("/auth/me");
    },
};

const ApiProfil = {
    async moi() {
        return apiFetch("/profils/moi");
    },
    async update(data) {
        return apiFetch("/profils/moi", { method: "PUT", body: JSON.stringify(data) });
    },
    async completion() {
        return apiFetch("/profils/moi/completion");
    },
};

const ApiOffres = {
    async list(search) {
        const suffix = search ? `?search=${encodeURIComponent(search)}` : "";
        return apiFetch(`/offres/${suffix}`);
    },
    async get(id) {
        return apiFetch(`/offres/${id}`);
    },
    async recommandees() {
        return apiFetch("/offres/recommandees");
    },
};

const ApiQuiz = {
    async envoyer(reponses) {
        return apiFetch("/quiz/envoyer", {
            method: "POST",
            body: JSON.stringify({ reponses }),
        });
    },
    async monDernier() {
        return apiFetch("/quiz/mon-dernier");
    },
};

function formaterDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    return d.toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" });
}

function requireAuth() {
    const page = window.location.pathname.split("/").pop() || "index.html";
    if (PROTECTED_PAGES.includes(page) && !Auth.isLoggedIn()) {
        window.location.replace("signup.html");
        return false;
    }
    return true;
}

const CHIP_COLORS = ["orange", "purple", "yellow", "blue", "green"];

function renderJobCard(offer, variant = "job") {
    const cls = variant === "offer" ? "offer-card" : "job-card";
    const mainCls = variant === "offer" ? "offer-main" : "job-main";
    const copyCls = variant === "offer" ? "offer-copy" : "job-copy";
    const tag = (offer.type_contrat || "stage").toLowerCase();
    const meta = [offer.localisation, offer.type_contrat, offer.domaine].filter(Boolean).join(" · ");

    if (variant === "offer") {
        return `
            <article class="${cls}" data-tags="${tag}">
                <a class="${mainCls}" href="detail-offre.html?id=${offer.id}">
                    <span class="dot green"></span>
                    <span class="${copyCls}">
                        <h3>${offer.titre}</h3>
                        <p>${offer.entreprise_nom || "Entreprise"}</p>
                        <span>${meta}</span>
                    </span>
                </a>
                <a class="arrow" href="detail-offre.html?id=${offer.id}" aria-label="Voir ${offer.titre}">
                    <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <path d="m9 18 6-6-6-6" />
                    </svg>
                </a>
            </article>`;
    }

    return `
        <article class="${cls}">
            <a class="${mainCls}" href="detail-offre.html?id=${offer.id}">
                <span class="dot"></span>
                <span class="${copyCls}">
                    <h3>${offer.titre}</h3>
                    <p>${offer.entreprise_nom || "Entreprise"}</p>
                    <span>${meta}</span>
                </span>
            </a>
            <a class="pill-action" href="detail-offre.html?id=${offer.id}">Postuler</a>
        </article>`;
}

async function initHomePage() {
    const banner = document.querySelector(".banner");
    const jobList = document.querySelector(".job-list");
    const sectionTitle = document.querySelector(".section-title");
    if (!banner || !jobList) return;

    try {
        const [completion, profil] = await Promise.all([
            ApiProfil.completion(),
            ApiProfil.moi().catch(() => null),
        ]);

        const pct = completion.pourcentage;
        const progressSpan = banner.querySelector(".progress span");
        const bannerSmall = banner.querySelector("small");
        const bannerH1 = banner.querySelector("h1");

        bannerSmall.textContent = `Profil complété à ${pct}%`;
        if (progressSpan) {
            progressSpan.style.width = `${pct}%`;
            progressSpan.style.background = completion.complet ? "#49db80" : "var(--green)";
        }
        if (completion.complet) {
            banner.classList.add("banner-complete");
        }
        bannerH1.textContent = completion.conseil;

        if (!completion.peut_recommander) {
            sectionTitle.textContent = "Recommandé pour toi";
            jobList.innerHTML = `
                <section class="white-card card-block" style="padding:24px;text-align:center;">
                    <p style="color:var(--muted);font-size:14px;line-height:1.6;margin-bottom:16px;">
                        Tu veux des offres qui te correspondent ? Passe un court quiz pour avoir des recommandations personnalisées.
                    </p>
                    <a href="questionnaire.html" class="pill-action" style="display:inline-flex;text-decoration:none;">Faire le quiz →</a>
                </section>`;
            return;
        }

        const offres = await ApiOffres.recommandees();
        if (!offres.length) {
            jobList.innerHTML = `<p class="hint">Aucune offre recommandée pour le moment. Consulte toutes les offres disponibles.</p>`;
            return;
        }

        jobList.innerHTML = offres.map((o) => renderJobCard(o, "job")).join("");
        document.querySelectorAll(".pill-action").forEach((button) => {
            button.addEventListener("click", (e) => {
                if (button.textContent.trim() === "Postuler") {
                    e.preventDefault();
                    button.textContent = "Postulé";
                    button.style.background = "#49db80";
                }
            });
        });
    } catch (err) {
        console.error(err);
    }
}

async function initProfilPage() {
    const hero = document.querySelector(".profile-hero");
    if (!hero) return;

    try {
        const [profil, completion] = await Promise.all([
            ApiProfil.moi(),
            ApiProfil.completion(),
        ]);

        const nameEl = hero.querySelector("h1");
        const subEl = hero.querySelector(".profile-head p");
        const pctLabel = hero.querySelector(".label-strong");
        const progressSpan = hero.querySelector(".progress span");

        nameEl.textContent = `${profil.prenom} ${profil.nom}`.trim();
        const formation = [profil.formation, profil.universite].filter(Boolean).join(" · ");
        subEl.textContent = formation || profil.universite || "Étudiant Afiri";

        pctLabel.textContent = `Profil complété à ${completion.pourcentage}%`;
        if (progressSpan) {
            progressSpan.style.width = `${completion.pourcentage}%`;
            progressSpan.style.background = completion.complet ? "#49db80" : "var(--green)";
        }

        renderEditableSection("competences", "Compétences", profil.competences, "Ex: React, Python, SQL (séparés par des virgules)");
        renderEditableSection("experiences", "Expériences", profil.experiences, "Décris tes expériences professionnelles...");
        renderEditableSection("projets", "Projets", profil.projets, "Projets sur lesquels tu as travaillé...");

        const copyBtn = document.querySelector("[data-copy-profile]");
        if (copyBtn) {
            copyBtn.addEventListener("click", () => {
                const url = `${window.location.origin}${window.location.pathname.replace("profil.html", "")}profil-public.html?id=${profil.lien_partage}`;
                navigator.clipboard.writeText(url).then(() => {
                    copyBtn.textContent = "Lien copié !";
                    setTimeout(() => { copyBtn.textContent = "Copier le lien du profil"; }, 2000);
                });
            });
        }
    } catch (err) {
        console.error(err);
    }
}

function renderEditableSection(key, title, value, placeholder) {
    let section = document.querySelector(`[data-profile-section="${key}"]`);
    if (!section) return;

    const chips = key === "competences";
    const display = value || "";
    const chipsHtml = chips && display
        ? display.split(",").map((c, i) => {
            const color = CHIP_COLORS[i % CHIP_COLORS.length];
            return `<span class="chip ${color}">${c.trim()}</span>`;
        }).join("")
        : `<p class="profile-empty">${placeholder}</p>`;

    section.innerHTML = `
        <div class="profile-section-head">
            <h2>${title}</h2>
            <button type="button" class="profile-edit-btn" data-edit="${key}">Modifier</button>
        </div>
        <div class="profile-display" data-display="${key}">${chips ? `<div class="chips">${chipsHtml}</div>` : `<p>${display || placeholder}</p>`}</div>
        <div class="profile-edit-form hidden" data-form="${key}">
            <textarea class="auth-input" rows="3" placeholder="${placeholder}">${display}</textarea>
            <button type="button" class="pill-action profile-save-btn" data-save="${key}">Enregistrer</button>
        </div>`;

    section.querySelector(`[data-edit="${key}"]`).addEventListener("click", () => {
        section.querySelector(`[data-display="${key}"]`).classList.add("hidden");
        section.querySelector(`[data-form="${key}"]`).classList.remove("hidden");
    });

    section.querySelector(`[data-save="${key}"]`).addEventListener("click", async () => {
        const textarea = section.querySelector("textarea");
        const newVal = textarea.value.trim();
        try {
            await ApiProfil.update({ [key]: newVal });
            renderEditableSection(key, title, newVal, placeholder);
            const completion = await ApiProfil.completion();
            const pctLabel = document.querySelector(".label-strong");
            const progressSpan = document.querySelector(".profile-hero .progress span");
            if (pctLabel) pctLabel.textContent = `Profil complété à ${completion.pourcentage}%`;
            if (progressSpan) {
                progressSpan.style.width = `${completion.pourcentage}%`;
                progressSpan.style.background = completion.complet ? "#49db80" : "var(--green)";
            }
        } catch (err) {
            alert(err.message || "Erreur lors de la sauvegarde");
        }
    });
}

async function initOffresPage() {
    const list = document.querySelector(".offer-list");
    if (!list) return;

    try {
        const offres = await ApiOffres.list();
        if (!offres.length) {
            list.innerHTML = `<p class="hint">Aucune offre disponible pour le moment.</p>`;
            return;
        }
        list.innerHTML = offres.map((o) => renderJobCard(o, "offer")).join("");
    } catch (err) {
        console.error(err);
    }
}

async function loadOfferDetailFromApi(offerId) {
    const detailPage = document.querySelector("[data-offer-detail]");
    if (!detailPage || !offerId) return false;

    try {
        const offer = await ApiOffres.get(offerId);
        document.title = `Afiri - ${offer.titre}`;
        detailPage.querySelector("[data-offer-title]").textContent = offer.titre;
        detailPage.querySelector("[data-offer-company]").textContent =
            `${offer.entreprise_nom || "Entreprise"} · ${offer.localisation || "Cameroun"}`;
        detailPage.querySelector("[data-offer-deadline]").textContent =
            `${offer.type_contrat || "Candidature"} · ${offer.domaine || ""}`;
        detailPage.querySelector("[data-offer-description]").textContent = offer.description;
        detailPage.querySelector("[data-offer-match]").textContent =
            `Domaine : ${offer.domaine || "Général"} — ${offer.type_contrat || "Offre"}`;
        detailPage.querySelector("[data-offer-advice]").textContent =
            "“Complète ton profil et passe le quiz pour améliorer tes recommandations.”";
        return true;
    } catch (err) {
        console.error(err);
        return false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const page = window.location.pathname.split("/").pop() || "index.html";
    if (PROTECTED_PAGES.includes(page)) {
        if (!requireAuth()) return;
    }
    if (page === "app.html") initHomePage();
    if (page === "profil.html") initProfilPage();
    if (page === "offres.html") initOffresPage();
});
