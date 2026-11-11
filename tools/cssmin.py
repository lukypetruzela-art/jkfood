"""Zmenšení stylů pro web: odstraní pravidla, jejichž třídy/ID se na žádné stránce nepoužívají,
komentáře a zbytečné mezery. Zdrojový soubor assets/styles.css zůstává čitelný a beze změny."""
import re


def _blocks(css):
    """Rozdělí CSS na položky nejvyšší úrovně: (prelude, body) nebo (prelude, None) pro @import apod."""
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        k = css.find(";", i)
        if j < 0:
            break
        if 0 <= k < j and css[i:k].strip().startswith("@"):
            out.append((css[i:k].strip(), None)); i = k + 1; continue
        depth, e = 1, j + 1
        while depth and e < n:
            if css[e] == "{": depth += 1
            elif css[e] == "}": depth -= 1
            e += 1
        out.append((css[i:j].strip(), css[j + 1:e - 1]))
        i = e
    return out


def _split_selectors(prelude):
    parts, depth, cur = [], 0, ""
    for ch in prelude:
        if ch in "([": depth += 1
        elif ch in ")]": depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur); cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def _alive(sel, tokens):
    # pseudo-třídy :not()/:is() s neznámou třídou nevadí – kontrolují se jen "povinné" třídy a ID
    core = re.sub(r":(?:not|is|where|has)\([^)]*\)", "", sel)
    core = re.sub(r"\[[^\]]*\]", "", core)
    for name in re.findall(r"[.#](-?[A-Za-z_][\w-]*)", core):
        if name not in tokens:
            return False
    return True


def _purge(css, tokens):
    out = []
    for prelude, body in _blocks(css):
        if body is None:
            out.append(prelude + ";"); continue
        if prelude.startswith("@media") or prelude.startswith("@supports"):
            inner = _purge(body, tokens)
            if inner.strip():
                out.append(prelude + "{" + inner + "}")
        elif prelude.startswith("@"):
            out.append(prelude + "{" + body + "}")          # @font-face, @keyframes…
        else:
            sels = [s for s in _split_selectors(prelude) if _alive(s, tokens)]
            if sels:
                out.append(",".join(sels) + "{" + body + "}")
    return "".join(out)


def minify(css, tokens):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = _purge(css, tokens)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};:,>])\s*", r"\1", css)
    css = css.replace(";}", "}")
    # mezera za dvojtečkou uvnitř selektorů (např. "a :hover") se nikde nepoužívá; ve složených hodnotách zůstává
    return css.strip()


def tokens_from_html(html):
    html = re.sub(r"<style>.*?</style>", " ", html, flags=re.S)
    html = re.sub(r'<script type="application/ld\+json">.*?</script>', " ", html, flags=re.S)
    return set(re.findall(r"[A-Za-z_][\w-]*", html))
