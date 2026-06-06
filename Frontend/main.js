document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".pill-action, .wide-action").forEach((button) => {
        button.addEventListener("click", () => {
            if (button.textContent.trim() === "Postuler") {
                button.textContent = "Postulé";
                button.style.background = "#49db80";
            }
        });
    });


    // --- ANIMATIONS DE NAVIGATION ET PAGE ---
    const navItems = document.querySelectorAll(".bottom-nav .nav-item");
    const screen = document.querySelector(".screen");

    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            const href = item.getAttribute("href");
            if (item.classList.contains("active") || !href) return;
            e.preventDefault();

            const currentActive = document.querySelector(".bottom-nav .nav-item.active .nav-icon");
            const newIcon = item.querySelector(".nav-icon");

            if (currentActive && newIcon) {
                const startRect = currentActive.getBoundingClientRect();
                
                // Create a floating circle for smooth sliding
                const circle = document.createElement("div");
                circle.style.position = "fixed";
                circle.style.left = startRect.left + "px";
                circle.style.top = startRect.top + "px";
                circle.style.width = startRect.width + "px";
                circle.style.height = startRect.height + "px";
                circle.style.background = "var(--orange)";
                circle.style.borderRadius = "50%";
                circle.style.border = "5px solid #fff";
                circle.style.boxShadow = "0 0 0 5px rgba(255, 63, 39, 0.14), 0 10px 18px rgba(255, 63, 39, 0.34)";
                circle.style.transition = "all 0.35s cubic-bezier(0.2, 0.8, 0.2, 1)";
                circle.style.zIndex = "100";
                circle.style.pointerEvents = "none";
                document.body.appendChild(circle);

                // Hide original
                currentActive.style.opacity = "0";

                // Swap active state to get exact final position
                document.querySelectorAll(".bottom-nav .nav-item").forEach(i => {
                    i.classList.remove("active");
                    const ico = i.querySelector(".nav-icon");
                    if (ico) ico.style.opacity = "1";
                });
                item.classList.add("active");
                newIcon.style.opacity = "0";

                const endRect = newIcon.getBoundingClientRect();

                // Animate to new position
                setTimeout(() => {
                    circle.style.left = endRect.left + "px";
                    circle.style.top = endRect.top + "px";
                    circle.style.width = endRect.width + "px";
                    circle.style.height = endRect.height + "px";
                }, 10);
            }

            if (screen) screen.classList.add("page-exit");

            setTimeout(() => {
                window.location.href = href;
            }, 300);
        });
    });

    // Handle normal links for page exit animation
    document.querySelectorAll("a:not(.nav-item)").forEach(link => {
        link.addEventListener("click", (e) => {
            const href = link.getAttribute("href");
            if (!href || href.startsWith("#") || href.startsWith("mailto") || link.target === "_blank") return;
            e.preventDefault();
            if (screen) screen.classList.add("page-exit");
            setTimeout(() => window.location.href = href, 300);
        });
    });

    initOfferDetail();
    initQuiz();
});

const offerDetails = {
    "front-end-react": {
        title: "Stage Front-end React",
        company: "Mboa Digital",
        location: "Douala, Cameroun",
        deadline: "Jusqu'au 15 juin",
        duration: "Stage 3 mois",
        description: "Participe à la création d'interfaces web simples, rapides et lisibles pour des clients locaux. HTML/CSS requis, React apprécié.",
        match: "Ton profil est compatible: React, UI et projets web étudiants.",
        advice: "Mets en avant tes projets même académiques, et ajoute un lien de mini-CV propre."
    },
    "assistant-rh": {
        title: "Assistant RH junior",
        company: "Kamer Talent",
        location: "Yaoundé, Cameroun",
        deadline: "Candidature ouverte",
        duration: "Alternance",
        description: "Aide l'équipe RH à trier les candidatures, planifier les entretiens et suivre les profils juniors pour des missions locales.",
        match: "Ton profil est compatible: organisation, communication et outils bureautiques.",
        advice: "Montre ta rigueur, ta capacité à communiquer et une expérience de travail en équipe."
    },
    "data-trainee": {
        title: "Data trainee",
        company: "AgroLink",
        location: "Akwa, Douala",
        deadline: "Jusqu'au 22 juin",
        duration: "Stage 2 mois",
        description: "Nettoie des tableaux, prépare des rapports simples et aide l'équipe à mieux lire les données agricoles avec Excel et SQL.",
        match: "Ton profil est compatible: Excel, logique, analyse et curiosité data.",
        advice: "Ajoute un petit projet Excel, un dashboard ou un exercice SQL dans ton mini-CV."
    },
    "community-manager": {
        title: "Community manager",
        company: "Canal Edu",
        location: "Buea, Cameroun",
        deadline: "Candidature ouverte",
        duration: "Temps partiel",
        description: "Prépare des publications, réponds à la communauté et propose des idées de contenus pour une plateforme éducative.",
        match: "Ton profil est compatible: créativité, rédaction et communication digitale.",
        advice: "Mets en avant une page, un visuel ou une campagne que tu as déjà animée."
    },
    "backend-node": {
        title: "Développeur Back-end Node",
        company: "TechNova",
        location: "Abidjan, Côte d'Ivoire",
        deadline: "Jusqu'au 30 juin",
        duration: "Stage 6 mois",
        description: "Travaille sur des API Node.js, participe à la conception de routes Express et aide à connecter les données au produit.",
        match: "Ton profil est compatible: JavaScript, logique API et bases backend.",
        advice: "Ajoute un lien GitHub avec une petite API propre et documentée."
    },
    "ui-ux-designer": {
        title: "UI/UX Designer",
        company: "Creatix Studio",
        location: "Yaoundé, Cameroun",
        deadline: "Jusqu'au 18 juillet",
        duration: "Stage 1 an",
        description: "Crée des maquettes Figma, améliore les parcours utilisateurs et prépare des prototypes pour des produits web et mobiles.",
        match: "Ton profil est compatible: Figma, UI, sens visuel et empathie utilisateur.",
        advice: "Ajoute deux maquettes propres avec une courte explication de tes choix."
    },
    "chef-projet-digital": {
        title: "Chef de Projet Digital",
        company: "Innovatech",
        location: "Lagos, Nigeria",
        deadline: "Candidature ouverte",
        duration: "Stage 9 mois",
        description: "Aide à suivre les tâches, organiser les priorités et coordonner les équipes autour de projets digitaux.",
        match: "Ton profil est compatible: organisation, gestion, communication et méthode Agile.",
        advice: "Présente un projet de groupe où tu as planifié, suivi ou coordonné le travail."
    },
    "marketing-digital": {
        title: "Consultant Marketing Digital",
        company: "MarketPro",
        location: "Accra, Ghana",
        deadline: "Jusqu'au 12 juillet",
        duration: "Stage 4 mois",
        description: "Participe à des campagnes SEO/SEM, analyse les performances et propose des améliorations pour attirer plus de clients.",
        match: "Ton profil est compatible: marketing, SEO, analyse et communication.",
        advice: "Ajoute une mini-campagne, une analyse de page ou un exemple de contenu optimisé."
    }
};

function initOfferDetail() {
    const detailPage = document.querySelector("[data-offer-detail]");
    if (!detailPage) return;

    const params = new URLSearchParams(window.location.search);
    const offerId = params.get("id") || "front-end-react";

    if (typeof loadOfferDetailFromApi === "function" && offerId && offerId.length > 20) {
        loadOfferDetailFromApi(offerId);
        return;
    }

    const offer = offerDetails[offerId] || offerDetails["front-end-react"];

    document.title = `Afiri - ${offer.title}`;
    detailPage.querySelector("[data-offer-title]").textContent = offer.title;
    detailPage.querySelector("[data-offer-company]").textContent = `${offer.company} · ${offer.location}`;
    detailPage.querySelector("[data-offer-deadline]").textContent = `${offer.deadline} · ${offer.duration}`;
    detailPage.querySelector("[data-offer-description]").textContent = offer.description;
    detailPage.querySelector("[data-offer-match]").textContent = offer.match;
    detailPage.querySelector("[data-offer-advice]").textContent = `“${offer.advice}”`;
}

function initQuiz() {
    const quiz = document.querySelector("[data-quiz]");
    if (!quiz) return;

    const questions = [
        {
            title: "Dans un projet de groupe, tu préfères...",
            answers: [
                { label: "Organiser les étapes et les rôles", type: "project", level: 2 },
                { label: "Créer les visuels et convaincre", type: "design", level: 2 },
                { label: "Analyser les données et décider", type: "data", level: 3 },
                { label: "Coder ou construire la solution", type: "dev", level: 3 }
            ]
        },
        {
            title: "Ton niveau actuel en outils numériques ressemble à...",
            answers: [
                { label: "Je découvre encore les bases", type: "support", level: 1 },
                { label: "Je peux faire un petit projet guidé", type: "dev", level: 2 },
                { label: "Je travaille déjà seul sur des projets", type: "dev", level: 3 },
                { label: "Je peux aider ou encadrer d'autres personnes", type: "project", level: 4 }
            ]
        },
        {
            title: "Quel type de mission te motive le plus ?",
            answers: [
                { label: "Créer une interface web ou mobile", type: "dev", level: 3 },
                { label: "Comprendre les utilisateurs et designer", type: "design", level: 2 },
                { label: "Traiter des fichiers, chiffres ou tableaux", type: "data", level: 2 },
                { label: "Animer une communauté ou une campagne", type: "marketing", level: 2 }
            ]
        },
        {
            title: "Pour commencer, tu préfères une offre...",
            answers: [
                { label: "Stage encadré et progressif", type: "support", level: 1 },
                { label: "Projet court avec objectifs clairs", type: "project", level: 2 },
                { label: "Mission technique avec challenge", type: "dev", level: 3 },
                { label: "Remote ou freelance junior", type: "marketing", level: 3 }
            ]
        }
    ];

    const labels = {
        dev: "Développement web / mobile",
        design: "UI/UX et création produit",
        data: "Data, Excel et analyse",
        project: "Gestion de projet digital",
        marketing: "Marketing digital / communauté",
        support: "Stage junior encadré"
    };

    const offerTypes = {
        dev: ["Stage Front-end React", "Intégrateur HTML/CSS", "Développeur web junior"],
        design: ["Assistant UI/UX", "Designer Figma junior", "Test utilisateur produit"],
        data: ["Data trainee", "Assistant analyse Excel", "Stagiaire reporting"],
        project: ["Assistant chef de projet", "Coordinateur digital junior", "Product assistant"],
        marketing: ["Community manager junior", "Assistant marketing digital", "Créateur de contenu"],
        support: ["Stage découverte tech", "Assistant informatique", "Support digital junior"]
    };

    const progressText = quiz.querySelector("[data-quiz-progress-text]");
    const progressBar = quiz.querySelector("[data-quiz-progress]");
    const stepText = quiz.querySelector("[data-quiz-step]");
    const questionTitle = quiz.querySelector("[data-quiz-question]");
    const answersBox = quiz.querySelector("[data-quiz-answers]");
    const panel = quiz.querySelector("[data-quiz-panel]");
    const backButton = quiz.querySelector("[data-quiz-back]");
    const nextButton = quiz.querySelector("[data-quiz-next]");

    let current = 0;
    const selected = [];

    function renderQuestion() {
        const question = questions[current];
        const percent = Math.round(((current + 1) / questions.length) * 100);

        progressText.textContent = `${percent}% complété`;
        progressBar.style.width = `${percent}%`;
        stepText.textContent = `Question ${current + 1} sur ${questions.length}`;
        questionTitle.textContent = question.title;
        nextButton.textContent = current === questions.length - 1 ? "Voir résultat" : "Continuer";
        backButton.textContent = current === 0 ? "Accueil" : "Retour";

        answersBox.innerHTML = question.answers.map((answer, index) => `
            <button class="answer${selected[current] === index ? " selected" : ""}" data-answer="${index}">
                <span class="num">${index + 1}</span>
                ${answer.label}
            </button>
        `).join("");

        answersBox.querySelectorAll("[data-answer]").forEach((answerButton) => {
            answerButton.addEventListener("click", () => {
                selected[current] = Number(answerButton.dataset.answer);
                renderQuestion();
            });
        });
    }

    const TYPE_TO_FILIERE = {
        dev: "informatique",
        design: "marketing",
        data: "informatique",
        project: "gestion",
        marketing: "marketing",
        support: "informatique",
    };

    async function saveQuizToBackend(payload) {
        if (typeof ApiQuiz === "undefined" || !Auth.isLoggedIn()) return;
        try {
            await ApiQuiz.envoyer(payload);
        } catch (err) {
            console.error("Erreur sauvegarde quiz:", err);
        }
    }

    function showResult() {
        const totals = {};
        let levelTotal = 0;

        selected.forEach((answerIndex, questionIndex) => {
            const answer = questions[questionIndex].answers[answerIndex];
            totals[answer.type] = (totals[answer.type] || 0) + 1;
            levelTotal += answer.level;
        });

        const bestType = Object.entries(totals).sort((a, b) => b[1] - a[1])[0]?.[0] || "support";
        const average = levelTotal / questions.length;
        const level = average < 1.8 ? "Débutant" : average < 2.8 ? "Intermédiaire" : "Junior avancé";

        saveQuizToBackend({
            type: bestType,
            filiere: TYPE_TO_FILIERE[bestType],
            level,
            complete: true,
            skipped: false,
            partial: false,
            answered_count: questions.length,
        });

        progressText.textContent = "100% complété";
        progressBar.style.width = "100%";
        panel.innerHTML = `
            <section class="quiz-result">
                <p class="quiz-kicker">Résultat du quiz</p>
                <h1>${level}</h1>
                <p class="result-copy">Ton profil correspond surtout à <strong>${labels[bestType]}</strong>. On peut te proposer des offres adaptées à ton niveau et à tes réponses.</p>
                <div class="result-card">
                    <span>Types d'offres recommandées</span>
                    ${offerTypes[bestType].map((offer) => `<b>${offer}</b>`).join("")}
                </div>
                <a class="result-link" href="app.html">Découvrir nos recommandations</a>
            </section>
        `;
        nextButton.textContent = "Recommencer";
        backButton.textContent = "Accueil";
    }

    backButton.addEventListener("click", async () => {
        if (panel.querySelector(".quiz-result")) {
            window.location.href = "app.html";
            return;
        }

        if (current === 0) {
            await saveQuizToBackend({ skipped: true, complete: false, partial: false });
            window.location.href = "app.html";
            return;
        }

        current -= 1;
        renderQuestion();
    });

    nextButton.addEventListener("click", () => {
        if (panel.querySelector(".quiz-result")) {
            current = 0;
            selected.length = 0;
            renderQuestion();
            return;
        }

        if (selected[current] === undefined) {
            answersBox.classList.add("shake");
            setTimeout(() => answersBox.classList.remove("shake"), 260);
            return;
        }

        if (current === questions.length - 1) {
            showResult();
            return;
        }

        current += 1;
        renderQuestion();
    });

    renderQuestion();
}
