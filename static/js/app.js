// ---------------------------------------------------------
// Préférence d'affichage grille / tableau (mémorisée, partagée sur toutes les pages)
// ---------------------------------------------------------
document.addEventListener('alpine:init', () => {
  Alpine.store('vue', {
    mode: localStorage.getItem('vueAffichage') || 'grid',
    set(mode) {
      this.mode = mode;
      localStorage.setItem('vueAffichage', mode);
    }
  });
});

// ---------------------------------------------------------
// Gestion des modales (chargées dynamiquement via HTMX dans #modal-root)
// ---------------------------------------------------------
function fermerModal() {
  const root = document.getElementById('modal-root');
  if (root) root.innerHTML = '';
}

document.body.addEventListener('click', function (e) {
  if (e.target.classList && e.target.classList.contains('modal-overlay')) {
    fermerModal();
  }
});

document.body.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') fermerModal();
});

// Ferme la modale après une suppression réussie (HX-Trigger côté serveur)
document.body.addEventListener('produitSupprime', fermerModal);
document.body.addEventListener('clientSupprime', fermerModal);
document.body.addEventListener('fournisseurSupprime', fermerModal);
document.body.addEventListener('categorieSupprime', fermerModal);

// ---------------------------------------------------------
// Bouton retour (topbar des pages de détail)
// ---------------------------------------------------------
function retourPage(fallbackUrl) {
  // Si on arrive depuis une autre page du site (navigation interne), on utilise l'historique
  // du navigateur pour revenir exactement là où l'utilisateur était (avec ses filtres/recherche).
  // Sinon (lien direct, nouvel onglet...), on retombe sur l'URL de secours fournie par la page.
  const memeOrigine = document.referrer && document.referrer.startsWith(window.location.origin);
  if (memeOrigine && window.history.length > 1) {
    window.history.back();
  } else if (fallbackUrl) {
    window.location.href = fallbackUrl;
  } else {
    window.history.back();
  }
}

// ---------------------------------------------------------
// Gestion dynamique des lignes de formulaire (achats / ventes)
// ---------------------------------------------------------
function initFormsetLignes(conteneurId, prefixeVide) {
  const conteneur = document.getElementById(conteneurId);
  if (!conteneur) return;
  const totalForms = document.getElementById(`id_${prefixeVide}-TOTAL_FORMS`);

  conteneur.addEventListener('click', function (e) {
    const btn = e.target.closest('.ligne-remove');
    if (!btn) return;
    const row = btn.closest('.ligne-row');
    const deleteInput = row.querySelector('input[name$="-DELETE"]');
    if (deleteInput) {
      deleteInput.checked = true;
      row.style.display = 'none';
    } else {
      row.remove();
    }
    recalculerTotalLignes(conteneurId);
  });

  conteneur.addEventListener('input', function () {
    recalculerTotalLignes(conteneurId);
  });
}

function ajouterLigne(conteneurId, prefixeVide) {
  const conteneur = document.getElementById(conteneurId);
  const totalFormsInput = document.getElementById(`id_${prefixeVide}-TOTAL_FORMS`);
  const template = document.getElementById(`${conteneurId}-template`);
  if (!conteneur || !totalFormsInput || !template) return;

  const index = parseInt(totalFormsInput.value, 10);
  let html = template.innerHTML.replaceAll('__prefix__', index);
  const wrapper = document.createElement('tbody');
  wrapper.innerHTML = html;
  conteneur.appendChild(wrapper.firstElementChild);
  totalFormsInput.value = index + 1;
}

function recalculerTotalLignes(conteneurId) {
  const conteneur = document.getElementById(conteneurId);
  if (!conteneur) return;
  let total = 0;
  conteneur.querySelectorAll('.ligne-row').forEach(function (row) {
    if (row.style.display === 'none') return;
    const qteInput = row.querySelector('.ligne-qte');
    const prixInput = row.querySelector('.ligne-prix');
    const remiseInput = row.querySelector('.ligne-remise');
    const qte = parseFloat(qteInput && qteInput.value) || 0;
    const prix = parseFloat(prixInput && prixInput.value) || 0;
    const remise = parseFloat(remiseInput && remiseInput.value) || 0;
    total += qte * prix * (1 - remise / 100);
  });
  const totalEl = document.getElementById(`${conteneurId}-total`);
  if (totalEl) {
    totalEl.textContent = Math.round(total).toLocaleString('fr-FR').replaceAll(',', ' ') + ' FCFA (estimation HT)';
  }
}

// ---------------------------------------------------------
// Export PDF du tableau de bord (impression du navigateur → PDF)
// ---------------------------------------------------------
function exporterDashboardPDF() {
  window.print();
}