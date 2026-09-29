"""Bannières 1024×500 exigées par Google Play (« Image de présentation »). Rendu Chrome headless.
    python3 magasins/banniere.py
"""
import base64
import pathlib
import subprocess
import tempfile

ICI = pathlib.Path(__file__).resolve().parent
IMG = ICI.parent / "site/img"
POLICES = ICI.parent / "site/polices"

APPLIS = {
    "neuroforge": ("NEUROFORGE", "Neuf exercices pour garder l'esprit vif", "#050404", "#2a1a0e", "#f5a04a"),
    "reveil": ("Réveil", "L'alarme qu'on arrête en réussissant un défi", "#1a237e", "#3949ab", "#ffc107"),
}


def b64(p: pathlib.Path) -> str:
    return base64.b64encode(p.read_bytes()).decode()


for cle, (nom, accroche, fond1, fond2, accent) in APPLIS.items():
    html = f"""<html><head><style>
@font-face {{ font-family: F; src: url(data:font/woff2;base64,{b64(POLICES / 'fraunces-latin-wght-normal.woff2')}); font-weight: 100 900; }}
@font-face {{ font-family: I; src: url(data:font/woff2;base64,{b64(POLICES / 'inter-latin-wght-normal.woff2')}); font-weight: 100 900; }}
body {{ margin: 0; width: 1024px; height: 500px; overflow: hidden;
  background: linear-gradient(135deg, {fond1}, {fond2}); display: flex; align-items: center; gap: 56px; padding: 0 72px; box-sizing: border-box; }}
img {{ width: 260px; height: 260px; border-radius: 56px; box-shadow: 0 16px 40px rgb(0 0 0 / .45); }}
h1 {{ font: 400 76px/1 F; color: #fff; margin: 0 0 20px; }}
p {{ font: 500 30px/1.3 I; color: {accent}; margin: 0; max-width: 560px; }}
</style></head><body><img src="data:image/png;base64,{b64(IMG / f'{cle}-512.png')}"><div><h1>{nom}</h1><p>{accroche}</p></div></body></html>"""
    with tempfile.TemporaryDirectory() as d:
        f = pathlib.Path(d) / "b.html"
        f.write_text(html)
        sortie = ICI / cle / "banniere-1024x500.png"
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--window-size=1024,500", f"--screenshot={sortie}", f.as_uri()], check=True, capture_output=True)
    print(sortie)
