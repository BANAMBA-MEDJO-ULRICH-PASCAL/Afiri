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
        const onAuthPage = /signup\.html|index\.html$/.test(window.location.pathname);
        if (!onAuthPage) {
            sessionStorage.setItem("afiri_session_expired", "1");
            window.location.href = "signup.html";
        }
        throw new Error("Session expirée. Reconnecte-toi.");
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

function showToast(message) {
    let toast = document.getElementById("afiriToast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "afiriToast";
        toast.className = "profile-toast";
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2800);
}

const CHIP_COLORS = ["orange", "purple", "yellow", "blue", "green"];

function getOfferTags(offer) {
    const tags = new Set();
    const tc = (offer.type_contrat || "").toLowerCase();
    const loc = (offer.localisation || "").toLowerCase();
    const desc = (offer.description || "").toLowerCase();

    if (tc.includes("stage")) tags.add("stage");
    if (tc.includes("alternance") || tc.includes("partiel")) tags.add("partiel");
    if (tc.includes("cdi") || tc.includes("cdd") || tc.includes("plein")) tags.add("plein");
    if (loc.includes("remote") || desc.includes("remote") || desc.includes("télétravail")) tags.add("remote");

    if (!tags.size) tags.add("tous");
    return Array.from(tags).join(" ");
}

function renderJobCard(offer, variant = "job") {
    const cls = variant === "offer" ? "offer-card" : "job-card";
    const mainCls = variant === "offer" ? "offer-main" : "job-main";
    const copyCls = variant === "offer" ? "offer-copy" : "job-copy";
    const tags = getOfferTags(offer);
    const meta = [offer.localisation, offer.type_contrat, offer.domaine].filter(Boolean).join(" · ");
    const searchText = [offer.titre, offer.entreprise_nom, offer.domaine, offer.localisation, offer.type_contrat]
        .filter(Boolean).join(" ").toLowerCase();

    if (variant === "offer") {
        return `
            <article class="${cls}" data-tags="${tags}" data-search="${searchText}">
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
        <article class="${cls}" data-tags="${tags}" data-search="${searchText}">
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

function applyOfferFilters() {
    const searchInput = document.querySelector(".search-input, .header-search input");
    const activeFilter = document.querySelector(".filter.active");
    const filterType = activeFilter ? activeFilter.textContent.toLowerCase().trim() : "tous";
    const searchValue = searchInput ? searchInput.value.toLowerCase().trim() : "";

    const cards = document.querySelectorAll(".job-card, .offer-card");
    let visible = 0;

    cards.forEach((card) => {
        const tags = card.dataset.tags || "";
        const searchData = card.dataset.search || card.textContent.toLowerCase();

        const matchesFilter = filterType === "tous" || tags.includes(filterType);
        const matchesSearch = !searchValue || searchData.includes(searchValue);

        const show = matchesFilter && matchesSearch;
        card.style.display = show ? "" : "none";
        if (show) visible += 1;
    });

    const emptyMsg = document.getElementById("offresEmptyMsg");
    if (emptyMsg) {
        emptyMsg.style.display = visible === 0 ? "block" : "none";
    }
}

function setupOfferSearchAndFilters() {
    const searchInput = document.querySelector(".search-input, .header-search input");
    if (searchInput && !searchInput.dataset.bound) {
        searchInput.dataset.bound = "1";
        searchInput.addEventListener("input", applyOfferFilters);
    }

    document.querySelectorAll(".filter").forEach((btn) => {
        if (btn.dataset.bound) return;
        btn.dataset.bound = "1";
        btn.addEventListener("click", () => {
            document.querySelectorAll(".filter").forEach((f) => f.classList.remove("active"));
            btn.classList.add("active");
            applyOfferFilters();
        });
    });

    applyOfferFilters();
}

function bindPostulerButtons() {
    document.querySelectorAll(".pill-action").forEach((button) => {
        if (button.dataset.bound) return;
        button.dataset.bound = "1";
        button.addEventListener("click", (e) => {
            if (button.textContent.trim() === "Postuler") {
                e.preventDefault();
                button.textContent = "Postulé";
                button.style.background = "#49db80";
            }
        });
    });
}

function renderJobList(container, offres, variant = "job") {
    if (!offres.length) {
        container.innerHTML = `<p class="hint">Aucune offre trouvée pour le moment.</p>`;
        return;
    }
    container.innerHTML = offres.map((o) => renderJobCard(o, variant)).join("");
    bindPostulerButtons();
    setupOfferSearchAndFilters();
}

async function initHomePage() {
    const banner = document.querySelector(".banner");
    const jobList = document.querySelector(".job-list");
    const sectionTitle = document.querySelector(".section-title");
    if (!banner || !jobList) return;

    try {
        const completion = await ApiProfil.completion();

        const progressSpan = banner.querySelector(".progress span");
        const bannerSmall = banner.querySelector("small");
        const bannerH1 = banner.querySelector("h1");

        bannerSmall.textContent = `Profil complété à ${completion.pourcentage}%`;
        if (progressSpan) {
            progressSpan.style.width = `${completion.pourcentage}%`;
            progressSpan.style.background = completion.complet ? "#49db80" : "var(--green)";
        }
        if (completion.complet) banner.classList.add("banner-complete");
        bannerH1.textContent = completion.conseil;

        if (!completion.peut_recommander) {
            jobList.innerHTML = `
                <section class="white-card card-block" style="padding:24px;text-align:center;">
                    <p style="color:var(--muted);font-size:14px;line-height:1.6;margin-bottom:16px;">
                        Tu veux des offres qui te correspondent ? Passe un court quiz pour avoir des recommandations personnalisées.
                    </p>
                    <a href="questionnaire.html" class="pill-action" style="display:inline-flex;text-decoration:none;">Faire le quiz →</a>
                </section>`;
            setupOfferSearchAndFilters();
            return;
        }

        let offres = [];
        try {
            offres = await ApiOffres.recommandees();
        } catch (recErr) {
            console.warn("Recommandations API:", recErr);
        }

        if (!offres || !offres.length) {
            const all = await ApiOffres.list();
            offres = all.slice(0, 8);
        }

        renderJobList(jobList, offres, "job");
    } catch (err) {
        console.error(err);
        jobList.innerHTML = `
            <p class="hint" style="color:var(--primary);">
                Impossible de charger les recommandations. <a href="offres.html" style="color:var(--primary);font-weight:700;">Voir toutes les offres →</a>
            </p>`;
    }
}

/* ── Profil : modal d'édition ── */
let profileModalState = { key: null, title: null, placeholder: null };

function ensureProfileModal() {
    if (document.getElementById("profileEditModal")) return;

    const overlay = document.createElement("div");
    overlay.id = "profileEditModal";
    overlay.className = "profile-modal-overlay";
    overlay.innerHTML = `
        <div class="profile-modal" role="dialog" aria-modal="true">
            <div class="profile-modal-header">
                <h3 id="profileModalTitle">Modifier</h3>
                <button type="button" class="profile-modal-close" id="profileModalClose" aria-label="Fermer">×</button>
            </div>
            <textarea id="profileModalTextarea" placeholder=""></textarea>
            <div class="profile-modal-actions">
                <button type="button" class="profile-modal-cancel" id="profileModalCancel">Annuler</button>
                <button type="button" class="profile-modal-save" id="profileModalSave">Enregistrer</button>
            </div>
        </div>`;
    document.body.appendChild(overlay);

    const close = () => overlay.classList.remove("open");
    overlay.addEventListener("click", (e) => { if (e.target === overlay) close(); });
    document.getElementById("profileModalClose").addEventListener("click", close);
    document.getElementById("profileModalCancel").addEventListener("click", close);

    document.getElementById("profileModalSave").addEventListener("click", async () => {
        const { key, title, placeholder } = profileModalState;
        if (!key) return;

        const newVal = document.getElementById("profileModalTextarea").value.trim();
        const saveBtn = document.getElementById("profileModalSave");
        saveBtn.disabled = true;
        saveBtn.textContent = "Enregistrement...";

        try {
            await ApiProfil.update({ [key]: newVal });
            close();
            renderEditableSection(key, title, newVal, placeholder);
            showToast("Modifications enregistrées ✓");

            const completion = await ApiProfil.completion();
            const pctLabel = document.querySelector(".label-strong");
            const progressSpan = document.querySelector(".profile-hero .progress span");
            if (pctLabel) pctLabel.textContent = `Profil complété à ${completion.pourcentage}%`;
            if (progressSpan) {
                progressSpan.style.width = `${completion.pourcentage}%`;
                progressSpan.style.background = completion.complet ? "#49db80" : "var(--green)";
            }
        } catch (err) {
            showToast(err.message || "Erreur lors de la sauvegarde");
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = "Enregistrer";
        }
    });
}

function openProfileModal(key, title, value, placeholder) {
    ensureProfileModal();
    profileModalState = { key, title, placeholder };
    document.getElementById("profileModalTitle").textContent = title;
    document.getElementById("profileModalTextarea").value = value || "";
    document.getElementById("profileModalTextarea").placeholder = placeholder;
    document.getElementById("profileEditModal").classList.add("open");
    document.getElementById("profileModalTextarea").focus();
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
        if (copyBtn && !copyBtn.dataset.bound) {
            copyBtn.dataset.bound = "1";
            copyBtn.addEventListener("click", () => {
                const url = `${window.location.origin}${window.location.pathname.replace("profil.html", "")}profil-public.html?id=${profil.lien_partage}`;
                navigator.clipboard.writeText(url).then(() => showToast("Lien copié !"));
            });
        }
    } catch (err) {
        console.error(err);
        hero.querySelector("h1").textContent = "Session expirée";
        hero.querySelector(".profile-head p").textContent = "Reconnecte-toi pour voir ton profil.";
        showToast("Reconnecte-toi pour continuer");
        setTimeout(() => { window.location.href = "signup.html"; }, 2000);
    }
}

function renderEditableSection(key, title, value, placeholder) {
    const section = document.querySelector(`[data-profile-section="${key}"]`);
    if (!section) return;

    const chips = key === "competences";
    const display = value || "";

    let bodyHtml;
    if (chips && display) {
        bodyHtml = `<div class="chips">${display.split(",").map((c, i) => {
            const color = CHIP_COLORS[i % CHIP_COLORS.length];
            return `<span class="chip ${color}">${c.trim()}</span>`;
        }).join("")}</div>`;
    } else if (display) {
        bodyHtml = `<p>${display}</p>`;
    } else {
        bodyHtml = `<p class="profile-empty">${placeholder}</p>`;
    }

    section.innerHTML = `
        <div class="profile-section-head">
            <h2>${title}</h2>
            <button type="button" class="profile-edit-btn" data-edit="${key}">Modifier</button>
        </div>
        <div class="profile-display">${bodyHtml}</div>`;

    section.querySelector(`[data-edit="${key}"]`).addEventListener("click", () => {
        openProfileModal(key, title, display, placeholder);
    });
}

async function initOffresPage() {
    const list = document.querySelector(".offer-list");
    if (!list) return;

    try {
        const offres = await ApiOffres.list();
        list.innerHTML = `<p class="hint" id="offresEmptyMsg" style="display:none;">Aucune offre ne correspond à ta recherche.</p>`;
        const container = document.createElement("div");
        container.className = "offer-list-inner";
        list.appendChild(container);

        if (!offres.length) {
            container.innerHTML = `<p class="hint">Aucune offre disponible pour le moment.</p>`;
            return;
        }

        container.innerHTML = offres.map((o) => renderJobCard(o, "offer")).join("");
        setupOfferSearchAndFilters();
    } catch (err) {
        console.error(err);
        list.innerHTML = `<p class="hint" style="color:var(--primary);">Erreur de chargement. Recharge la page.</p>`;
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
    if (sessionStorage.getItem("afiri_session_expired")) {
        sessionStorage.removeItem("afiri_session_expired");
        setTimeout(() => showToast("Session expirée — reconnecte-toi"), 300);
    }

    const page = window.location.pathname.split("/").pop() || "index.html";
    if (PROTECTED_PAGES.includes(page)) {
        if (!requireAuth()) return;
    }
    if (page === "app.html") initHomePage();
    if (page === "profil.html") initProfilPage();
    if (page === "offres.html") initOffresPage();
});
