"""Small helpers to edit Jupyter notebook cell sources while keeping the
original JSON formatting (indent and ASCII escaping) so git diffs stay small."""
import json


def load(path):
    raw = open(path, encoding="utf-8").read()
    nb = json.loads(raw)
    for indent in (1, 2):
        for ascii_ in (False, True):
            if json.dumps(nb, indent=indent, ensure_ascii=ascii_) + "\n" == raw:
                return nb, (indent, ascii_)
    raise ValueError(f"cannot reproduce JSON formatting of {path}")


def save(path, nb, fmt):
    indent, ascii_ = fmt
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(nb, indent=indent, ensure_ascii=ascii_) + "\n")


def get_src(cell):
    s = cell["source"]
    return "".join(s) if isinstance(s, list) else s


def set_src(cell, text):
    if isinstance(cell["source"], list):
        cell["source"] = text.splitlines(keepends=True)
    else:
        cell["source"] = text


def md_cell(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}
