"""Construit magasins/guide.html : la fiche de publication à ouvrir dans Chrome, un bouton Copier par champ.
    python3 magasins/guide.py && google-chrome magasins/guide.html
Les textes viennent de fiches.json : les modifier là, puis relancer.
"""
import html
import json
import pathlib

ICI = pathlib.Path(__file__).resolve().parent
F = json.loads((ICI / "fiches.json").read_text())
LIVRABLES = {
    "reveil": pathlib.Path.home() / "02_projects/reveil/livrables/1.0.1",
    "neuroforge": pathlib.Path.home() / "09_GAMING/neuroforge/livrables/natif/1.1.0",
}

ETAPES = """
<ol class="etapes">
<li><b>Créer le compte Google Play Console</b> : <a href="https://play.google.com/console/signup" target="_blank">play.google.com/console/signup</a>, frais uniques de 25 $ US.
  <div class="alerte">Deux choix de compte. <b>Personnel</b> : prêt tout de suite, mais Google exige un <b>test fermé de 14 jours avec au moins 12 testeurs</b>
  avant la mise en ligne publique. <b>Organisation</b> : pas de test obligatoire, mais il faut un numéro D-U-N-S (gratuit, quelques jours à quelques
  semaines) et une entreprise immatriculée. Tant que le NEQ d'Auxo Systems n'est pas confirmé, prenez <b>Personnel</b>.</div></li>
<li>Vérification d'identité (pièce + cellulaire). Comptez 1 à 3 jours.</li>
<li>Pour chaque appli ci-dessous : <b>Créer une appli</b> → langue par défaut Français (Canada) → Appli → Gratuite.</li>
<li>Remplir <b>Fiche principale</b> avec les boutons Copier, téléverser l'icône, la bannière et les captures.</li>
<li>Remplir <b>Contenu de l'appli</b> avec les réponses de la section « Questionnaires ».</li>
<li><b>Test fermé</b> → Créer une version → téléverser le fichier <code>.aab</code> indiqué → ajouter la liste de courriels des 12 testeurs →
  leur envoyer le lien d'inscription. Signature : laisser <b>Google gérer la clé</b> (choix par défaut).</li>
<li>Après 14 jours : <b>Production</b> → Promouvoir la version. Examen de Google : quelques heures à 7 jours.</li>
<li>Quand la page Play existe, <b>envoyez-moi son lien</b> : le bouton Installer de votre page y mènera, et l'installation deviendra automatique pour tout Android.</li>
</ol>"""


def bouton(texte: str) -> str:
    return f'<button onclick="copier(this)" data-t="{html.escape(texte, quote=True)}">Copier</button>'


def video(a: dict) -> str:
    """Formulaire « service de premier plan » + plan de la vidéo de démonstration (Réveil)."""
    v = a.get("video")
    if not v:
        return ""
    lignes = "".join(
        f"<tr><th>{html.escape(nom)}</th><td><pre>{html.escape(fr)}</pre>{bouton(fr)}</td>"
        f"<td>{'<pre>' + html.escape(en) + '</pre>' + bouton(en) if en else ''}</td></tr>"
        for nom, fr, en in v["champs"]
    )
    plan = "".join(f"<li>{html.escape(e)}</li>" for e in v["plan"])
    return f"""
<h3>Service de premier plan et vidéo de démonstration</h3>
<p>{html.escape(v['intro'])}</p>
<table><tr><th></th><th>Français</th><th>English (si le formulaire est en anglais)</th></tr>{lignes}</table>
<h4>Plan de la vidéo (60 à 90 secondes)</h4><ol class="etapes">{plan}</ol>"""


def section(cle: str) -> str:
    a = F[cle]
    lignes = []
    for nom, fr, en in a["champs"]:
        lignes.append(
            f"<tr><th>{html.escape(nom)}</th><td><pre>{html.escape(fr)}</pre>{bouton(fr)}"
            f"<div class='nb'>{len(fr)} caractères</div></td>"
            f"<td>{'<pre>' + html.escape(en) + '</pre>' + bouton(en) if en else ''}</td></tr>"
        )
    rep = "".join(f"<tr><th>{html.escape(q)}</th><td colspan=2>{html.escape(r)}</td></tr>" for q, r in a["reponses"])
    caps = sorted((ICI / cle / "captures").glob("*.png"))
    images = "".join(f'<a href="{cle}/captures/{c.name}" target="_blank"><img src="{cle}/captures/{c.name}"></a>' for c in caps)
    aab = LIVRABLES[cle] / a["fichier_play"]
    return f"""
<section id="{cle}">
<h2><img class="ic" src="../site/img/{cle}-512.png"> {a['nom']}</h2>
<p class="fichier">Fichier à téléverser dans Play : <code>{aab}</code>
  <button onclick="copier(this)" data-t="{aab.parent}">Copier le dossier</button></p>
<h3>Fiche principale</h3>
<table><tr><th></th><th>Français (principal)</th><th>English (ajouter la traduction en-CA)</th></tr>{''.join(lignes)}</table>
<h3>Images</h3>
<p>Icône 512×512 : <code>site/img/{cle}-512.png</code> · Bannière 1024×500 : <code>magasins/{cle}/banniere-1024x500.png</code> · Captures de téléphone :</p>
<div class="caps"><a href="../site/img/{cle}-512.png" target="_blank"><img src="../site/img/{cle}-512.png"></a>
<a href="{cle}/banniere-1024x500.png" target="_blank"><img class="ban" src="{cle}/banniere-1024x500.png"></a>{images}</div>
<h3>Questionnaires (Contenu de l'appli)</h3>
<table>{rep}</table>{video(a)}
</section>"""


page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Publication — magasins d'applis</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{ margin: 0; font: 16px/1.6 system-ui, sans-serif; background: #fbfaf5; color: #1f2d2b; }}
header {{ background: #0f1c1a; color: #f4f1e8; padding: 24px 16px; }}
header h1 {{ margin: 0; font-weight: 500; }} header p {{ margin: 4px 0 0; color: #9db0a8; }}
nav {{ display: flex; gap: 10px; margin-top: 14px; flex-wrap: wrap; }}
nav a {{ background: #a9ddcf; color: #0f1c1a; padding: 10px 18px; border-radius: 10px; text-decoration: none; font-weight: 700; }}
main {{ max-width: 1200px; margin: 0 auto; padding: 16px; }}
h2 {{ display: flex; align-items: center; gap: 12px; font-weight: 500; font-size: 1.8rem; margin: 48px 0 8px; border-top: 3px solid #2c5a66; padding-top: 24px; }}
h4 {{ margin: 18px 0 4px; }}
h2 .ic {{ width: 48px; height: 48px; border-radius: 12px; }}
table {{ border-collapse: collapse; width: 100%; background: #fff; }}
th, td {{ border: 1px solid #dcd8cc; padding: 10px; vertical-align: top; text-align: left; }}
th {{ width: 22%; background: #f3f1e9; font-weight: 600; }}
pre {{ white-space: pre-wrap; font: inherit; margin: 0 0 8px; max-height: 260px; overflow: auto; }}
button {{ background: #2c5a66; color: #fff; border: 0; border-radius: 8px; padding: 8px 16px; font-weight: 700; cursor: pointer; }}
button.ok {{ background: #426b52; }}
.nb {{ font-size: .8rem; color: #4a5d52; margin-top: 4px; }}
.alerte {{ background: #fff4d6; border-left: 5px solid #8a6d1f; padding: 10px 14px; margin: 8px 0; }}
.etapes li {{ margin: 10px 0; }}
.caps {{ display: flex; gap: 10px; overflow-x: auto; padding-bottom: 8px; }}
.caps img {{ height: 280px; border-radius: 8px; border: 1px solid #dcd8cc; }}
.caps img.ban {{ height: 137px; }}
.fichier {{ background: #e8f4ef; padding: 10px 14px; border-radius: 8px; }}
code {{ background: #efede3; padding: 1px 5px; border-radius: 4px; }}
</style></head><body>
<header><h1>Publication sur les magasins d'applis</h1>
<p>Tout ce qu'il faut pour Google Play, dans l'ordre. Un bouton Copier par champ.</p>
<nav><a href="#ordre">1. Étapes</a><a href="#reveil">2. Réveil</a><a href="#neuroforge">3. NEUROFORGE</a><a href="#autres">4. Autres magasins</a></nav></header>
<main>
<h2 id="ordre">Étapes, dans l'ordre</h2>{ETAPES}
{section('reveil')}
{section('neuroforge')}
<h2 id="autres">Autres magasins</h2>
<ul>
<li><b>Apple App Store (NEUROFORGE seulement)</b> : compte Apple Developer, 99 $ US par an. Dites-moi quand il existe :
  la compilation iPhone est déjà prévue sur GitHub, il manque seulement les certificats du compte. D'ici là, sur iPhone,
  la version web s'installe depuis Safari (bouton sur votre page).</li>
<li><b>Réveil sur iPhone</b> : pas possible tel quel. Il faudrait réécrire la partie alarme pour iOS (AlarmKit, iOS 26) et avoir un Mac.</li>
<li><b>Microsoft Store (NEUROFORGE)</b> : compte développeur Microsoft, puis « Appli MSI ou EXE » avec le lien de l'installateur
  de votre page. À faire après Google Play.</li>
</ul>
</main>
<script>
function copier(b) {{
  navigator.clipboard.writeText(b.dataset.t).then(() => {{
    const t = b.textContent; b.textContent = 'Copié ✓'; b.classList.add('ok');
    setTimeout(() => {{ b.textContent = t; b.classList.remove('ok'); }}, 1500);
  }});
}}
</script></body></html>"""

(ICI / "guide.html").write_text(page)
print(ICI / "guide.html")
for cle in F:
    for nom, fr, en in F[cle]["champs"][:2]:
        limite = 30 if "30" in nom else 80
        for t in (fr, en):
            assert len(t) <= limite, (cle, nom, t, len(t))
