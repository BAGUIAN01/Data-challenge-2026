"""Remove comments and docstrings from Python source, keeping the first line of the module docstring."""
import ast
import io
import sys
import tokenize


def epurer(src, garder_entete=True):
    tree = ast.parse(src)
    lines = src.splitlines()
    drop, keep_head = set(), None
    nodes = [tree] + [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    for n in nodes:
        body = n.body
        if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                and isinstance(body[0].value.value, str):
            d = body[0]
            if n is tree and garder_entete:
                para = " ".join(d.value.value.strip().split("\n\n")[0].split())
                keep_head = para.split(". ")[0].rstrip(".")
                keep_head += "" if keep_head.endswith(("?", "!")) else "."
            drop.update(range(d.lineno - 1, d.end_lineno))
    cut = {}
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            r, c = tok.start
            cut[r - 1] = min(c, cut.get(r - 1, c))
    out = []
    for i, ln in enumerate(lines):
        if i in drop:
            continue
        if i in cut:
            if ln[:cut[i]].strip() == "":
                continue
            ln = ln[:cut[i]].rstrip()
        out.append(ln)
    text = "\n".join(out)
    while "\n\n\n\n" in text:
        text = text.replace("\n\n\n\n", "\n\n\n")
    text = text.strip("\n") + "\n"
    if keep_head:
        text = f'"""{keep_head}"""\n' + text
    ast.parse(text)
    return text


if __name__ == "__main__":
    for f in sys.argv[1:]:
        s = open(f, encoding="utf-8").read()
        open(f, "w", encoding="utf-8").write(epurer(s))
