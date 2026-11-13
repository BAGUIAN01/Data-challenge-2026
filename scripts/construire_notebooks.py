"""Build and run the notebooks of the project, one per step, from the scripts."""
import ast
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent
TIDY, REF, A = "data/tidy/presco_tidy.csv", "data/ref/regions_13_17.csv", "analyse/"

NOTEBOOKS = {
    "02_nettoyage": ("Étape 2 · Nettoyage", "Lecture du fichier du challenge, contrôles de cohérence, sources externes.", [
        ("parse_presco", "Lecture du fichier du challenge", ["data/raw/Presco.txt", TIDY]),
        ("check_presco", "Contrôles de cohérence", [TIDY]),
        ("prepare_facteurs", "Sources externes : faim, EDS, déplacés", []),
    ]),
    "03_transformation": ("Étape 3 · Transformation", "Référentiel des régions, panel région × année, violence, carte.", [
        ("referentiel_officiel", "Correspondance officielle 13 / 17 régions", ["data/raw/externe/hdx_cod_ab/bfa_admin_boundaries.xlsx", "data/ref/"]),
        ("regions_2025", "Noms des régions de 2025", [REF, TIDY, "data/tidy/presco_tidy_regions2025.csv"]),
        ("analyse_pistes", "Panel région × année et pistes P1 à P7", [TIDY, A]),
        ("regions_2025", "Panel avec les régions de 2025", [REF, "analyse/panel_region_annee.csv", "analyse/panel_region_annee_2025.csv"]),
        ("acled_anticipation", "Violence : agrégat ACLED par région et année scolaire",
         ["data/raw/externe/hdx_acled/acled_political_violence_month_year.xlsx", "analyse/panel_region_annee.csv", A]),
        ("carte_13_regions", "Carte des 13 régions", ["data/raw/externe/hdx_cod_ab/geojson/bfa_admin1.geojson", REF, A]),
    ]),
    "04a_analyse_descriptive": ("Étape 4 · Analyse descriptive", "Ce que disent les données du challenge, et les figures des pistes.", [
        ("analyse_presco", "Analyse descriptive", [TIDY, A]),
        ("figures_pistes", "Figures 01 à 07", [TIDY, A, "analyse/figures/"]),
    ]),
    "04b_modeles": ("Étape 4 · Modèles", "Prévision, alerte, apprentissage automatique, facteurs, formule du risque, score global, facteur dominant.", [
        ("prevision_hypothese", "Prévision 2025/26, alerte d'escalade, test de l'hypothèse", []),
        ("figures_prevision", "Figures de la prévision", []),
        ("machine_learning", "Apprentissage automatique contre règles simples", []),
        ("figures_ml", "Figures de l'apprentissage automatique", []),
        ("approches_prevision", "Écoles ouvertes et filière des cohortes", []),
        ("solution_prevision", "Où, combien, matrice de priorité 2026/27", []),
        ("facteurs_decrochage", "Facteurs autres que l'insécurité", []),
        ("prevision_facteurs", "Les facteurs aident-ils à prévoir ?", []),
        ("anticipation_fine", "Signaux fins de violence et calendrier d'alerte", []),
        ("formule_risque", "Formule du risque", []),
        ("score_global", "Score global", []),
        ("facteur_dominant", "Facteur dominant : sur quoi agir", []),
    ]),
    "05_interpretation": ("Étape 5 · Interprétation", "Figures de la solution, données du tableau de bord, fiches régionales.", [
        ("figures_approches", "Figures 13 à 17", []),
        ("export_tableau_de_bord", "Données du tableau de bord", []),
        ("fiches_regionales", "Fiches régionales", []),
    ]),
}

PATHS_SETUP = """root = Path.cwd()
while not (root / "scripts").is_dir() and root != root.parent:
    root = root.parent
os.chdir(root)
sys.path.insert(0, "scripts")"""

FIGURES = '''def show_figures(since, folders=("analyse/figures", "analyse", "analyse/fiches"), limit=8):
    views = sorted((p for d in folders for p in Path(d).glob("*.png") if p.stat().st_mtime >= since), key=lambda p: p.name)
    for p in views[:limit]:
        print(p)
        display(Image(filename=str(p), width=760))'''

SCRIPTS = {p.stem for p in (ROOT / "scripts").glob("*.py")}


def is_setup_statement(n):
    """Import, or a setting that belongs with the imports (matplotlib backend, search path)."""
    if isinstance(n, (ast.Import, ast.ImportFrom)):
        return True
    return isinstance(n, ast.Expr) and ast.unparse(n).startswith(("matplotlib.use(", "sys.path.insert("))


def imports_cell(names):
    """One cell with every import of the notebook: standard library, then packages, then the project's scripts."""
    plain_imports, modules = set(), {}
    base = [ast.parse("import os\nimport sys\nimport time\nfrom pathlib import Path\nfrom IPython.display import Image, display")]
    trees = base + [ast.parse((ROOT / "scripts" / f"{n}.py").read_text(encoding="utf-8")) for n in names]
    for t in trees:
        for n in t.body:
            if isinstance(n, ast.Import):
                for a in n.names:
                    plain_imports.add((a.name, a.asname))
            elif isinstance(n, ast.ImportFrom):
                modules.setdefault(n.module, set()).update((a.name, a.asname) for a in n.names)
    group_of = lambda m: 2 if m.split(".")[0] in SCRIPTS else 0 if m.split(".")[0] in sys.stdlib_module_names else 1
    lines_out = {0: [], 1: [], 2: []}
    for m, a in sorted(plain_imports):
        lines_out[group_of(m)].append((m, f"import {m}" + (f" as {a}" if a else "")))
    for m, ns in sorted(modules.items()):
        names_m = ", ".join(n + (f" as {a}" if a else "") for n, a in sorted(ns))
        lines_out[group_of(m)].append((m, f"from {m} import {names_m}"))
    packages = [l for _, l in sorted(lines_out[1], key=lambda x: (x[0] != "matplotlib", x[0], x[1].startswith("from")))]
    if any(l == "import matplotlib" for l in packages):
        packages.insert(packages.index("import matplotlib") + 1, 'matplotlib.use("Agg")')
    blocs = ["\n".join(l for _, l in sorted(lines_out[0], key=lambda x: (x[1].startswith("from"), x[0]))), "\n".join(packages), PATHS_SETUP]
    if lines_out[2]:
        blocs.append("\n".join(l for _, l in sorted(lines_out[2])))
    return "\n\n".join(b for b in blocs if b)


def script_cells(name):
    src = (ROOT / "scripts" / f"{name}.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    lines_out = src.splitlines()
    blocs, current = [], []
    for n in tree.body:
        if is_setup_statement(n):
            continue
        if isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant) and isinstance(n.value.value, str):
            continue
        if isinstance(n, ast.If) and "__name__" in ast.unparse(n.test):
            continue
        text = "\n".join(lines_out[(n.decorator_list[0].lineno if getattr(n, "decorator_list", None) else n.lineno) - 1:n.end_lineno])
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            if current:
                blocs.append("\n".join(current)); current = []
            blocs.append(text)
        else:
            current.append(text)
    if current:
        blocs.append("\n".join(current))
    return blocs


def build_notebook(file_name, title, lead, steps):
    notebook = nbformat.v4.new_notebook()
    notebook.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    notebook.cells.append(nbformat.v4.new_markdown_cell(
        f"# {title}\n\n{lead}\n\nÀ lancer dans le projet complet (archive `05-interpretation_D1_scientist_projet-complet_v1.zip`), "
        "avec les données brutes placées comme le dit `data/raw/LISEZ-MOI.md`."))
    notebook.cells.append(nbformat.v4.new_code_cell(imports_cell(list(dict.fromkeys(e[0] for e in steps)))))
    notebook.cells.append(nbformat.v4.new_code_cell(FIGURES))
    seen = set()
    for i, (name, heading, args) in enumerate(steps, 1):
        notebook.cells.append(nbformat.v4.new_markdown_cell(f"## {i}. {heading}\n\n`scripts/{name}.py`"))
        alias = ""
        if name not in seen:
            for c in script_cells(name):
                notebook.cells.append(nbformat.v4.new_code_cell(c))
            seen.add(name)
            alias = f"run_{name} = main\n"
        notebook.cells.append(nbformat.v4.new_code_cell(
            f"{alias}t0 = time.time()\nsys.argv = {[name + '.py'] + args!r}\nrun_{name}()\nshow_figures(t0)"))
    return notebook


def main():
    out_dir = ROOT / "notebooks"
    out_dir.mkdir(exist_ok=True)
    selected = sys.argv[1:] or list(NOTEBOOKS)
    for f in selected:
        notebook = build_notebook(f, *NOTEBOOKS[f])
        NotebookClient(notebook, timeout=3600, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
        nbformat.write(notebook, out_dir / f"{f}.ipynb")
        print("cahier :", out_dir / f"{f}.ipynb")


if __name__ == "__main__":
    main()
