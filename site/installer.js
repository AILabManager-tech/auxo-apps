// Page de téléchargement : détecte l'appareil, affiche LE bon bouton Installer et la liste complète.
// Les versions et noms de fichiers viennent de versions.json (écrit par publier.sh) : rien à éditer ici
// quand une nouvelle version sort.

const DEPOT = "https://github.com/AILabManager-tech/auxo-apps/releases/download";

// ---------- Langue ----------
let langue = "fr";
try { langue = localStorage.getItem("langue") || (navigator.language || "fr").slice(0, 2); } catch { /* stockage bloqué */ }
if (langue !== "en") langue = "fr";
const T = (fr, en) => (langue === "en" ? en : fr);

function appliquerLangue() {
  document.documentElement.lang = langue;
  document.querySelectorAll("[data-en]").forEach((el) => {
    if (!el.dataset.fr) el.dataset.fr = el.innerHTML;
    el.innerHTML = langue === "en" ? el.dataset.en : el.dataset.fr;
  });
  const b = document.querySelector(".langue");
  if (b) b.textContent = langue === "en" ? "Français" : "English";
}

// ---------- Appareil ----------
function appareil() {
  const ua = navigator.userAgent;
  if (/iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1)) return "ios";
  if (/Android/.test(ua)) return "android";
  if (/CrOS/.test(ua)) return "chromeos";
  if (/Windows/.test(ua)) return "windows";
  if (/Macintosh|Mac OS X/.test(ua)) return "mac";
  if (/Linux/.test(ua)) return "linux";
  return "autre";
}

const NOMS = {
  android: "Android", ios: "iPhone / iPad", windows: "Windows", mac: "Mac", linux: "Linux",
  chromeos: "Chromebook", autre: T("cet appareil", "this device"),
};

const ICONE_DL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12m0 0-5-5m5 5 5-5M4 20h16"/></svg>';

// Étapes montrées après le clic, par système.
function etapes(os, nomAppli) {
  const e = {
    android: [
      T("Ouvrez le fichier téléchargé (notification ou dossier Téléchargements).", "Open the downloaded file (notification or Downloads folder)."),
      T("Si Android le demande, touchez <b>Paramètres</b> puis activez <b>Autoriser depuis cette source</b>, et revenez.", "If Android asks, tap <b>Settings</b>, turn on <b>Allow from this source</b>, then go back."),
      T("Touchez <b>Installer</b>, puis <b>Ouvrir</b>.", "Tap <b>Install</b>, then <b>Open</b>."),
    ],
    windows: [
      T("Ouvrez le fichier téléchargé.", "Open the downloaded file."),
      T("Si Windows affiche « Windows a protégé votre ordinateur », cliquez <b>Informations complémentaires</b> puis <b>Exécuter quand même</b>.", "If Windows shows “Windows protected your PC”, click <b>More info</b> then <b>Run anyway</b>."),
      T(`L'installation se fait seule ; ${nomAppli} apparaît dans le menu Démarrer.`, `Setup runs by itself; ${nomAppli} appears in the Start menu.`),
    ],
    mac: [
      T("Ouvrez le fichier .dmg téléchargé et glissez l'appli dans <b>Applications</b>.", "Open the downloaded .dmg and drag the app into <b>Applications</b>."),
      T("Au premier lancement : <b>clic droit</b> sur l'appli, puis <b>Ouvrir</b>, puis <b>Ouvrir</b> encore.", "First launch: <b>right-click</b> the app, choose <b>Open</b>, then <b>Open</b> again."),
      T("Sur macOS 15 et plus : Réglages Système → Confidentialité et sécurité → <b>Ouvrir quand même</b>.", "On macOS 15+: System Settings → Privacy & Security → <b>Open Anyway</b>."),
    ],
    linux: [
      T("Ubuntu, Debian, Mint : double-cliquez le fichier .deb, ou <code>sudo apt install ./fichier.deb</code>.", "Ubuntu, Debian, Mint: double-click the .deb, or <code>sudo apt install ./file.deb</code>."),
      T("Autres distributions : prenez l'AppImage (tableau plus bas), rendez-la exécutable et lancez-la.", "Other distributions: take the AppImage (table below), make it executable and run it."),
    ],
    ios: [
      T("Ouvrez cette page dans <b>Safari</b>.", "Open this page in <b>Safari</b>."),
      T("Touchez le bouton <b>Partager</b> (carré avec une flèche).", "Tap the <b>Share</b> button (square with an arrow)."),
      T("Choisissez <b>Sur l'écran d'accueil</b>, puis <b>Ajouter</b>. L'appli s'ouvre ensuite comme les autres, même hors ligne.", "Choose <b>Add to Home Screen</b>, then <b>Add</b>. It then opens like any app, even offline."),
    ],
  };
  return e[os] || [];
}

function afficherEtapes(os, nomAppli) {
  const boite = document.getElementById("etapes");
  const liste = etapes(os, nomAppli);
  if (!boite || !liste.length) return;
  boite.innerHTML = `<h2>${T("Pour terminer l'installation", "To finish installing")}</h2><ol>${liste.map((l) => `<li>${l}</li>`).join("")}</ol>`;
  boite.classList.add("visible");
}

// ---------- Rendu d'une page d'appli ----------
function url(appli, fichier) {
  return `${DEPOT}/${appli.tag}/${fichier}`;
}

function choixPrincipal(id, appli, os) {
  const f = appli.fichiers;
  const m = appli.magasins || {};
  if (os === "android") {
    if (m.play) return { href: m.play, texte: T("Installer depuis Google Play", "Get it on Google Play"), magasin: true };
    return { href: url(appli, f.android), texte: T("Installer sur Android", "Install on Android") };
  }
  if (os === "ios") {
    if (m.appstore) return { href: m.appstore, texte: T("Installer depuis l'App Store", "Get it on the App Store"), magasin: true };
    if (appli.web) return { href: appli.web, texte: T("Ouvrir et ajouter à l'écran d'accueil", "Open and add to Home Screen"), ios: true };
    return null;
  }
  if (os === "windows" && f.windows) {
    if (m.microsoft) return { href: m.microsoft, texte: T("Installer depuis le Microsoft Store", "Get it from the Microsoft Store"), magasin: true };
    return { href: url(appli, f.windows), texte: T("Installer sur Windows", "Install on Windows") };
  }
  if (os === "mac" && f.mac) return { href: url(appli, f.mac), texte: T("Installer sur Mac", "Install on Mac") };
  if (os === "linux" && f.linux_deb) return { href: url(appli, f.linux_deb), texte: T("Installer sur Linux (.deb)", "Install on Linux (.deb)") };
  if (appli.web) return { href: appli.web, texte: T("Ouvrir la version web", "Open the web version") };
  return null;
}

const LIGNES = [
  ["android", "Android", "APK"],
  ["android_32", T("Android (ancien appareil 32 bits)", "Android (older 32-bit device)"), "APK"],
  ["windows", "Windows 10 / 11", T("Installateur (.exe)", "Installer (.exe)")],
  ["windows_msi", "Windows 10 / 11", T("Paquet MSI (entreprises)", "MSI package (IT)")],
  ["mac", "macOS 10.15+", T("Image disque (.dmg), Intel et Apple Silicon", "Disk image (.dmg), Intel and Apple Silicon")],
  ["linux_deb", "Ubuntu / Debian", ".deb"],
  ["linux_rpm", "Fedora / openSUSE", ".rpm"],
  ["linux_appimage", "Linux", T("AppImage (toutes distributions)", "AppImage (any distribution)")],
];

function rendreAppli(id, appli) {
  const os = appareil();
  const zone = document.getElementById("installer");
  const choix = choixPrincipal(id, appli, os);
  const sous = document.getElementById("sous-bouton");

  if (choix) {
    zone.innerHTML = `<a class="installer" href="${choix.href}" ${choix.magasin || choix.href === appli.web ? "" : "download"}>${ICONE_DL}<span>${choix.texte}</span></a>`;
    zone.querySelector("a").addEventListener("click", () => afficherEtapes(choix.ios ? "ios" : os, appli.nom));
    sous.textContent = T(`Version ${appli.version} · détecté : ${NOMS[os]}`, `Version ${appli.version} · detected: ${NOMS[os]}`);
    if (choix.ios) afficherEtapes("ios", appli.nom);
  } else {
    zone.innerHTML = `<p class="installer" style="cursor:default">${T(`${appli.nom} fonctionne sur Android`, `${appli.nom} runs on Android`)}</p>`;
    sous.textContent = T("Scannez le code QR avec un cellulaire Android pour l'installer.", "Scan the QR code with an Android phone to install it.");
  }

  // Tableau complet : toutes les versions, quel que soit l'appareil.
  const corps = document.getElementById("fichiers");
  if (corps) {
    const lignes = LIGNES.filter(([cle]) => appli.fichiers[cle]).map(([cle, sys, type]) =>
      `<tr><td>${sys}</td><td>${type}</td><td><a href="${url(appli, appli.fichiers[cle])}" download>${T("Télécharger", "Download")}</a></td></tr>`);
    if (appli.web) lignes.push(`<tr><td>iPhone / iPad, ${T("navigateur", "browser")}</td><td>${T("Version web installable", "Installable web app")}</td><td><a href="${appli.web}">${T("Ouvrir", "Open")}</a></td></tr>`);
    corps.innerHTML = lignes.join("");
  }
}

// ---------- Démarrage ----------
async function demarrer() {
  appliquerLangue();
  document.querySelector(".langue")?.addEventListener("click", () => {
    langue = langue === "en" ? "fr" : "en";
    try { localStorage.setItem("langue", langue); } catch { /* stockage bloqué */ }
    location.reload();
  });

  const id = document.body.dataset.appli;
  if (!id) return;
  const racine = document.body.dataset.racine || "../";
  try {
    const v = await (await fetch(`${racine}versions.json`, { cache: "no-cache" })).json();
    rendreAppli(id, v[id]);
  } catch {
    document.getElementById("sous-bouton").textContent = T("Liste des versions indisponible : réessayez dans un instant.", "Version list unavailable: try again shortly.");
  }
}

demarrer();
