#!/usr/bin/env python3
"""Publie une version d'une appli sur la page de téléchargement.

    ./publier.py neuroforge 1.1.0 ~/09_GAMING/neuroforge/livrables/natif/1.1.0
    ./publier.py reveil 1.0.0 ~/02_projects/reveil/apps/mobile/build/app/outputs/flutter-apk

Ce que ça fait, dans l'ordre :
1. crée la release GitHub « <appli>-v<version> » dans ce dépôt, avec les installateurs du dossier ;
2. met à jour site/versions.json (la page lit ce fichier : aucun HTML à retoucher) ;
3. NEUROFORGE : recopie la version web (PWA) dans site/neuroforge/app ;
4. régénère les codes QR ; committe et pousse → GitHub Pages redéploie tout seul.

Les .aab ne sont pas publiés ici : ils vont au Play Store (dossier magasins/).
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys

ICI = pathlib.Path(__file__).resolve().parent
SITE = ICI / "site"
DEPOT = "AILabManager-tech/auxo-apps"
URL_SITE = "https://ailabmanager-tech.github.io/auxo-apps/"
PWA_NEUROFORGE = pathlib.Path.home() / "09_GAMING/neuroforge/app"

NOMS = {"neuroforge": "NEUROFORGE", "reveil": "Réveil"}

# Motif du nom de fichier → clé lue par installer.js
MOTIFS = [
    (r"arm64-v8a.*\.apk$|android\.apk$", "android"),
    (r"armeabi-v7a.*\.apk$", "android_32"),
    (r"-setup\.exe$", "windows"),
    (r"\.msi$", "windows_msi"),
    (r"\.dmg$", "mac"),
    (r"\.deb$", "linux_deb"),
    (r"\.rpm$", "linux_rpm"),
    (r"\.AppImage$", "linux_appimage"),
]


def sh(*cmd, **kw):
    print("$", " ".join(map(str, cmd)))
    return subprocess.run(cmd, check=True, **kw)


def collecter(appli: str, version: str, dossier: pathlib.Path, tmp: pathlib.Path) -> dict:
    """Associe chaque installateur à sa clé ; renomme ceux de Flutter (app-arm64-v8a-release.apk)."""
    fichiers = {}
    for f in sorted(dossier.iterdir()):
        for motif, cle in MOTIFS:
            if re.search(motif, f.name) and cle not in fichiers:
                nom = f.name
                if f.name.startswith("app-"):  # sortie Flutter
                    abi = "arm64" if cle == "android" else "armv7"
                    nom = f"Reveil-{version}-android-{abi}.apk"
                shutil.copy2(f, tmp / nom)
                fichiers[cle] = nom
                break
    if not fichiers:
        sys.exit(f"Aucun installateur reconnu dans {dossier}")
    return fichiers


def qr(nom: str, url: str) -> None:
    img = SITE / "img"
    sh("qrencode", "-t", "SVG", "-m", "2", "-l", "M", "--svg-path", "-o", str(img / f"qr-{nom}.svg"), url)
    # Version imprimable (affiches, publicités) : 1200 px.
    sh("qrencode", "-t", "PNG", "-m", "4", "-l", "M", "-s", "30", "-o", str(ICI / "publicite" / f"qr-{nom}.png"), url)


def main() -> None:
    if len(sys.argv) != 4 or sys.argv[1] not in NOMS:
        sys.exit(__doc__)
    appli, version, dossier = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3]).expanduser()
    tag = f"{appli}-v{version}"
    tmp = ICI / ".envoi" / tag
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)

    fichiers = collecter(appli, version, dossier, tmp)
    print("Installateurs :", json.dumps(fichiers, indent=1, ensure_ascii=False))

    existe = subprocess.run(["gh", "release", "view", tag, "-R", DEPOT], capture_output=True).returncode == 0
    if existe:
        sh("gh", "release", "upload", tag, "-R", DEPOT, "--clobber", *map(str, tmp.iterdir()))
    else:
        sh("gh", "release", "create", tag, "-R", DEPOT, "--title", f"{NOMS[appli]} {version}",
           "--notes", f"{NOMS[appli]} {version}. Page d'installation : {URL_SITE}{appli}/",
           "--latest=false", *map(str, tmp.iterdir()))
    shutil.rmtree(tmp.parent, ignore_errors=True)

    chemin = SITE / "versions.json"
    versions = json.loads(chemin.read_text()) if chemin.exists() else {}
    ancien = versions.get(appli, {})
    versions[appli] = {
        "nom": NOMS[appli],
        "version": version,
        "tag": tag,
        "fichiers": fichiers,
        "magasins": ancien.get("magasins", {"play": None, "appstore": None, "microsoft": None}),
        "web": "app/" if appli == "neuroforge" else None,
    }
    chemin.write_text(json.dumps(versions, indent=2, ensure_ascii=False) + "\n")

    if appli == "neuroforge":
        cible = SITE / "neuroforge/app"
        shutil.rmtree(cible, ignore_errors=True)
        shutil.copytree(PWA_NEUROFORGE, cible)

    (ICI / "publicite").mkdir(exist_ok=True)
    qr("accueil", URL_SITE)
    for a in NOMS:
        qr(a, f"{URL_SITE}{a}/")

    sh("git", "-C", str(ICI), "add", "-A")
    sh("git", "-C", str(ICI), "commit", "-qm", f"{NOMS[appli]} {version} publiée")
    sh("git", "-C", str(ICI), "push", "-q", "origin", "main")
    print(f"\nEn ligne dans 1-2 min : {URL_SITE}{appli}/")


if __name__ == "__main__":
    main()
