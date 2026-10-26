"""POC | Buyer Actions > Release > Release Items List: filter and sort bug hunt.

Run: python BuyerActions_Release.py   (then python make_docx.py)
Each case runs in its own try/except; a system error is logged and the next case continues.
"""
import os, re, json, time, datetime, itertools, collections
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "shots")
os.makedirs(SHOTS, exist_ok=True)
BASE = "https://engineering.ultrivalms.com/POC"
ITEMS_URL = BASE + "/BuyerAction/ReleaseItems"
USER, PWD = "buyeruser", "Ultriva!23"

COLS = ["RYG", "QKCItemNo", "Description", "IsConsignmentItem", "TotalCardCount", "TotalCardQty"]
LABEL = {"RYG": "RYG", "QKCItemNo": "Item", "Description": "Description", "IsConsignmentItem": "Is Consignment",
         "TotalCardCount": "Total Cards", "TotalCardQty": "Total Qty"}
NUMERIC = {"TotalCardCount", "TotalCardQty"}
AGING = [("$", "All"), ("ANC", "Not cycled"), ("A0", "Aged 0 Days"), ("A1", "Aged 1 Days"), ("A2", "Aged 2 Days"),
         ("A3", "Aged 3 Days"), ("A4", "Aged 4 Days"), ("A5", "Aged 5 Days"), ("AP", "Aged > 5 Days")]
SHOW = [("I", "Items List"), ("C", "Cards List"), ("MI", "My Items List"), ("MC", "My Cards List")]
COLOR = {"R": "Red", "Y": "Yellow", "G": "Green"}

results, side = [], collections.defaultdict(list)
counter = {"n": int(os.environ.get("START", "0"))}
ONLY = [a for a in os.environ.get("ONLY", "").split(",") if a]  # re-run only these areas
OUT = os.environ.get("OUT", "results.json")
CUR = {"dirty": False}


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


o = Options()
o.add_argument("--window-size=1920,1080")
o.add_experimental_option("excludeSwitches", ["enable-logging"])
d = webdriver.Chrome(options=o)
d.implicitly_wait(1)


def js(script, *a):
    return d.execute_script(script, *a)


def shot(name):
    p = os.path.join(SHOTS, f"{name}.png")
    try:
        d.save_screenshot(p)
    except Exception:
        return ""
    return p


def sys_error():
    try:
        t = js("return document.body.innerText.slice(0,1500).toLowerCase()")
    except Exception:
        return False
    return any(x in t for x in ("system error", "server error", "http error", "an error occurred", "an error has occurred"))


class SysErr(Exception):
    pass


def login():
    d.get(BASE + "/")
    d.find_element(By.ID, "UserName").send_keys(USER)
    d.find_element(By.ID, "Password").send_keys(PWD)
    d.find_element(By.ID, "login-button").click()
    time.sleep(3)


def paging():
    return norm(js("return ((document.querySelector('.ag-paging-panel')||{}).innerText||'')"))


def wait_grid(timeout=10):
    time.sleep(1.0)
    end = time.time() + timeout
    while time.time() < end:
        if sys_error():
            raise SysErr("System Error!! page displayed (URL: %s)" % d.current_url)
        p = paging()
        if p and ("of" in p) and js("return !!document.querySelector('.ag-center-cols-container .ag-row')") or "0 to 0 of 0" in p:
            return
        if js("return !!document.querySelector('.ag-overlay-no-rows-center')"):
            return
        time.sleep(0.4)


def load():
    d.get(ITEMS_URL)
    wait_grid()
    CUR["dirty"] = False


def total_reported():
    m = re.search(r"of (\d+) Page", paging())
    return int(m.group(1)) if m else 0


def page_rows():
    js("var v=document.querySelector('.ag-body-viewport');if(v)v.scrollTop=0")
    time.sleep(0.2)
    seen = {}
    for _ in range(60):
        for r in js("""var out=[];document.querySelectorAll('.ag-center-cols-container .ag-row').forEach(r=>{
            var o={_i:parseInt(r.getAttribute('row-index'))};
            r.querySelectorAll('.ag-cell').forEach(c=>{var k=c.getAttribute('col-id');if(!k)return;o[k]=c.innerText.trim();
              var im=c.querySelector('img');if(im)o[k+'_img']=(im.getAttribute('src')||'').split('/').pop();});
            out.push(o)});return out"""):
            seen[r["_i"]] = r
        info = js("var v=document.querySelector('.ag-body-viewport');var t=v.scrollTop;v.scrollTop=t+v.clientHeight*0.8;return [t,v.scrollTop]")
        time.sleep(0.12)
        if info[0] == info[1]:
            break
    return [seen[k] for k in sorted(seen)]


def pager_click(ref):
    return js("var b=document.querySelector('[data-ref=\"%s\"],[ref=\"%s\"]');if(!b||b.classList.contains('ag-disabled'))return false;b.click();return true" % (ref, ref))


def read_all():
    """All rows across pages, in displayed order; re-read if the grid was still rendering."""
    for attempt in range(3):
        out = read_pages()
        if len(out) == total_reported():
            return out
        time.sleep(1.0)
    side["count_mismatch"].append((CUR.get("label", ""), total_reported(), len(out)))
    return out


def read_pages():
    out = []
    pager_click("btFirst")
    time.sleep(0.5)
    for _ in range(10):
        out += page_rows()
        if not pager_click("btNext"):
            break
        time.sleep(0.5)
    pager_click("btFirst")
    time.sleep(0.2)
    return out


def chips():
    return [norm(x) for x in js("return [...document.querySelectorAll('#ulac_SUP_REL li.acfb-data span')].map(s=>s.innerText)")]


def type_supplier(text, want=None):
    """Type in the supplier box and pick the suggestion matching `want` (default: first)."""
    lis = []
    for _ in range(2):
        js("var i=document.getElementById('SUP_REL');i.value='';i.focus();")
        ActionChains(d).send_keys(text).perform()
        end = time.time() + 5
        while time.time() < end and not lis:
            time.sleep(0.4)
            lis = [l for l in d.find_elements(By.CSS_SELECTOR, "#SUP_REL_container_ac_results li") if norm(l.text)]
        if lis:
            break
    pick = None
    for li in lis:
        t = norm(li.text)
        if (want is None) or t.lower() == want.lower():
            pick = li
            break
    if pick is None:
        raise RuntimeError(f"Supplier suggestion '{want or text}' not found in {[norm(l.text) for l in lis][:6]}")
    name = norm(pick.text)
    pick.click()
    time.sleep(0.5)
    return name


def ensure_supplier(sup):
    """sup: 'supnew' -> only Supnew, 'ALL' -> no supplier restriction, anything else = typed text."""
    cur = [c.lower() for c in chips()]
    if sup == "ALL":
        if cur and "all suppliers" not in cur[0]:
            js("document.querySelectorAll('#ulac_SUP_REL .acpimg').forEach(x=>x.click())")
            time.sleep(0.3)
        return
    label = {"supnew": "Supnew (Supnew)"}.get(sup, sup)
    if cur == [label.lower()]:
        return
    js("document.querySelectorAll('#ulac_SUP_REL .acpimg').forEach(x=>x.click())")
    time.sleep(0.3)
    type_supplier(label[:6], label)


def set_filters(sup="supnew", do="$", so="I", cat="FK", ryg="RYG"):
    ensure_supplier(sup)
    js("""var s=document.getElementById('FILTER_DO');s.value=arguments[0];s.dispatchEvent(new Event('change',{bubbles:true}));
          var t=document.getElementById('FILTER_SO');t.value=arguments[1];t.dispatchEvent(new Event('change',{bubbles:true}));""", do, so)
    for sid, want, full in (("FILTER_CAT", cat, "FK"), ("FILTER_RYG", ryg, "RYG")):
        want = "" if sorted(want) == sorted(full) else want  # nothing ticked means All
        d.find_element(By.ID, "ddcl-" + sid).click()
        time.sleep(0.3)
        for i, ch in enumerate(full if sid == "FILTER_CAT" else "RYG"):
            cb = d.find_element(By.ID, f"ddcl-{sid}-i{i}")
            if cb.is_selected() != (ch in want):
                cb.click()
        d.find_element(By.ID, "ddcl-" + sid).click()
        time.sleep(0.2)
        got = "".join(js("return [...document.getElementById(arguments[0]).selectedOptions].map(o=>o.value)", sid))
        if sorted(got) != sorted(want):
            raise RuntimeError(f"Could not set {sid}: wanted {want}, selected {got}")
    js("document.querySelector('.btn-filter-submit-item').click()")
    wait_grid()


def items(rows):
    return {r.get("QKCItemNo") for r in rows}


def by_item(rows):
    return {r.get("QKCItemNo"): r for r in rows}


def num(s):
    try:
        return float(re.sub(r"[^\d.\-]", "", s or "") or 0)
    except ValueError:
        return 0.0


def case(area, title, steps, expected, fn):
    if ONLY and area not in ONLY:
        return None
    counter["n"] += 1
    cid = f"TC_{counter['n']:03d}"
    CUR["label"] = cid
    rec = dict(id=cid, area=area, title=title, steps=steps, expected=expected, actual="", status="PASS", shot="")
    for attempt in (1, 2):
        try:
            ok, actual = fn()
            rec["actual"] = actual
            if sys_error():
                raise SysErr("System Error!! page displayed (URL: %s)" % d.current_url)
            rec["status"] = "PASS" if ok else "FAIL"
            if not ok:
                rec["shot"] = shot(cid)
            break
        except SysErr as e:
            if attempt == 1:
                try:
                    load_default()
                except Exception:
                    pass
                continue
            rec["status"] = "SYSERR"
            rec["actual"] = str(e)
            rec["shot"] = shot(cid)
        except Exception as e:
            rec["status"] = "SKIP"
            rec["actual"] = "Automation error, case skipped: " + norm(str(e))[:200]
            rec["shot"] = shot(cid)
            break
    if rec["status"] in ("SYSERR", "SKIP"):
        try:
            load_default()
        except Exception:
            pass
    print(cid, rec["status"], area, "|", title, "|", rec["actual"][:150], flush=True)
    results.append(rec)
    return rec


def load_default():
    d.get(ITEMS_URL)
    time.sleep(2)
    CUR["dirty"] = False
    set_filters()


# ---------------------------------------------------------------- baseline
login()
load_default()
BASE_ROWS = read_all()
BASE_MAP = by_item(BASE_ROWS)
print("BASELINE rows", len(BASE_ROWS), "reported", total_reported(), flush=True)
shot("baseline")
RYG_IMG = {}  # color letter -> set of image names


def run(**kw):
    set_filters(**kw)
    return read_all()


def desc(kw):
    parts = []
    if kw.get("sup"):
        parts.append("Supplier")
    if kw.get("do", "$") != "$":
        parts.append("Cards=" + dict(AGING)[kw["do"]])
    if kw.get("so", "I") != "I":
        parts.append("Show=" + dict(SHOW)[kw["so"]])
    if kw.get("cat", "FK") != "FK":
        parts.append("Category=" + "+".join({"F": "Forecast", "K": "Kanban"}[c] for c in kw["cat"]))
    if kw.get("ryg", "RYG") != "RYG":
        parts.append("RYG=" + "+".join(COLOR[c] for c in kw["ryg"]))
    return ", ".join(parts)


SINGLE = {}  # key -> rows for reuse in combination checks


def single(key, **kw):
    if key not in SINGLE:
        SINGLE[key] = run(**kw)
    return SINGLE[key]


# ---------------------------------------------------------------- RYG filter
for c in "RYG":
    def f(c=c):
        r = run(ryg=c)
        SINGLE["ryg" + c] = r
        imgs = {x.get("RYG_img") for x in r}
        RYG_IMG[c] = imgs
        ok = bool(r) and len(imgs) == 1 and items(r) <= items(BASE_ROWS)
        return ok, f"{len(r)} rows, RYG images shown: {sorted(imgs)}; baseline {len(BASE_ROWS)} rows"
    case("Filter - RYG", f"RYG = {COLOR[c]} only", f"Select RYG = {COLOR[c]} only, click Go.",
         f"Only {COLOR[c]} rows are listed (single RYG indicator) and they exist in the unfiltered list.", f)


def f():
    allimgs = [RYG_IMG.get(c, set()) for c in "RYG"]
    disjoint = all(not (a & b) for a, b in itertools.combinations(allimgs, 2))
    n = sum(len(SINGLE.get("ryg" + c, [])) for c in "RYG")
    return disjoint and n == len(BASE_ROWS), f"R/Y/G row counts sum to {n}; baseline {len(BASE_ROWS)}; images disjoint: {disjoint}"
case("Filter - RYG", "Red + Yellow + Green partitions the full list", "Compare row counts of single-colour RYG filters with the unfiltered list.",
     "The three colour filters together return exactly all rows, with no row in two colours.", f)

for pair in ("RY", "RG", "YG"):
    def f(pair=pair):
        r = run(ryg=pair)
        exp = set().union(*(items(SINGLE.get("ryg" + c, [])) for c in pair))
        bad = {x.get("RYG_img") for x in r} - set().union(*(RYG_IMG.get(c, set()) for c in pair))
        return items(r) == exp and not bad, f"{len(items(r))} rows returned, expected {len(exp)}; unexpected indicators: {sorted(bad)}"
    case("Filter - RYG", "RYG = " + "+".join(COLOR[c] for c in pair), f"Select RYG {'+'.join(COLOR[c] for c in pair)}, click Go.",
         "Rows of both selected colours are listed and nothing else.", f)

# ---------------------------------------------------------------- Category filter
for cat, nm in (("F", "Forecast"), ("K", "Kanban")):
    def f(cat=cat, nm=nm):
        r = run(cat=cat)
        SINGLE["cat" + cat] = r
        return items(r) <= items(BASE_ROWS), f"{len(r)} rows for {nm}; baseline {len(BASE_ROWS)}; rows not in baseline: {sorted(items(r) - items(BASE_ROWS))[:5]}"
    case("Filter - Category", f"Category = {nm} only", f"Select Category = {nm} only, click Go.", f"Only {nm} items listed, all of them part of the unfiltered list.", f)


def f():
    r = run(cat="FK")
    u = items(SINGLE.get("catF", [])) | items(SINGLE.get("catK", []))
    return u == items(BASE_ROWS), f"Forecast ({len(items(SINGLE.get('catF', [])))}) + Kanban ({len(items(SINGLE.get('catK', [])))}) cover {len(u)} items; All shows {len(items(r))}"
case("Filter - Category", "Forecast + Kanban equals All", "Compare Forecast, Kanban and both categories.", "Forecast items plus Kanban items equal the unfiltered list.", f)

# ---------------------------------------------------------------- Cards (aging) filter
AGING_ROWS = {}
for v, nm in AGING[1:]:
    def f(v=v, nm=nm):
        r = run(do=v)
        AGING_ROWS[v] = r
        bad = [i for i, x in by_item(r).items() if i not in BASE_MAP or num(x.get("TotalCardCount")) > num(BASE_MAP[i].get("TotalCardCount"))]
        return not bad, f"{len(r)} rows, total cards {int(sum(num(x.get('TotalCardCount')) for x in r))}; items not in baseline or with more cards than unfiltered: {bad[:5]}"
    case("Filter - Cards", f"Cards = {nm}", f"Select Cards = {nm}, click Go.", "Rows are a subset of the unfiltered list and card counts never exceed the unfiltered counts.", f)


def f():
    tot = collections.Counter()
    for v, _ in AGING[1:]:
        for x in AGING_ROWS.get(v, []):
            tot[x.get("QKCItemNo")] += num(x.get("TotalCardCount"))
    diff = {i: (int(tot[i]), int(num(x.get("TotalCardCount")))) for i, x in BASE_MAP.items() if int(tot[i]) != int(num(x.get("TotalCardCount")))}
    return not diff, f"{len(diff)} item(s) where sum of aging buckets differs from All (bucket sum, All): {dict(list(diff.items())[:4])}"
case("Filter - Cards", "Sum of all aging buckets equals Cards = All", "Add Total Cards of every Cards option and compare with All.",
     "Every card falls in exactly one aging bucket, so per-item totals add up to the All value.", f)

# ---------------------------------------------------------------- Show
for v, nm in SHOW[1:]:
    def f(v=v, nm=nm):
        r = run(so=v)
        SINGLE["show" + v] = r
        if v == "MI":
            return items(r) <= items(BASE_ROWS), f"{len(r)} rows; My Items subset of Items List: {items(r) <= items(BASE_ROWS)}"
        return bool(js("return !!document.querySelector('.ag-root')")), f"{len(r)} rows, URL {d.current_url}"
    case("Filter - Show", f"Show = {nm}", f"Select Show = {nm}, click Go.", f"{nm} page opens with a grid and no error.", f)

# reset the saved Show preference
load_default()

# ---------------------------------------------------------------- Supplier (everything else runs with Supnew selected)
ALL_ROWS = []


def f():
    global ALL_ROWS
    ALL_ROWS = run(sup="ALL")
    r = run(sup="supnew")
    extra = sorted(items(r) - items(ALL_ROWS))[:5]
    return bool(r) and not extra and len(r) < len(ALL_ROWS), f"Supnew: {len(r)} rows; All Suppliers: {len(ALL_ROWS)} rows; Supnew items missing from All: {extra}"
case("Filter - Supplier", "Supplier = Supnew vs All Suppliers", "Select supplier Supnew (Supnew), click Go; then All Suppliers, click Go.",
     "Supnew shows only its own items, all of which also appear under All Suppliers.", f)


def f():
    r = run(sup="supnew")
    chip = chips()
    return len(chip) == 1 and "supnew" in chip[0].lower() and len(r) == len(BASE_ROWS), f"Chips {chip}; {len(r)} rows (baseline {len(BASE_ROWS)})"
case("Filter - Supplier", "Supplier chip and grid agree after Go", "Select Supnew, click Go.", "Only the Supnew chip is shown and the grid lists Supnew rows.", f)


def f():
    set_filters(sup="supnew")
    js("document.querySelectorAll('#ulac_SUP_REL .acpimg').forEach(x=>x.click())")
    time.sleep(0.4)
    type_supplier("supnew", "Supnew (Supnew)")
    type_supplier("Sup111", "Sup111023 (Sup111023)")
    chip = chips()
    js("document.querySelector('.btn-filter-submit-item').click()")
    wait_grid()
    r = read_all()
    other = run(sup="Sup111023 (Sup111023)")
    return len(chip) == 2 and items(r) == items(BASE_ROWS) | items(other), f"Chips {chip}; {len(r)} rows; Supnew alone {len(BASE_ROWS)} rows; Sup111023 alone {len(other)} rows"
case("Filter - Supplier", "Multiple suppliers (Supnew + Sup111023)", "Add a second supplier to Supnew, click Go.", "Rows of both suppliers are listed (union of the two single-supplier results).", f)


def f():
    js("document.querySelectorAll('#ulac_SUP_REL .acpimg').forEach(x=>x.click())")
    js("document.querySelector('.btn-filter-submit-item').click()")
    wait_grid()
    r = read_all()
    return items(r) == items(ALL_ROWS), f"No supplier chip: {len(r)} rows; All Suppliers {len(ALL_ROWS)} rows"
case("Filter - Supplier", "Removing the supplier chip returns all suppliers", "Remove the supplier chip, click Go.", "Behaves like All Suppliers or prompts to select a supplier.", f)
load_default()
# ---------------------------------------------------------------- Combinations
COMBOS = [
    ("RYG Green + Category Kanban", dict(ryg="G", cat="K")),
    ("RYG Green + Category Forecast", dict(ryg="G", cat="F")),
    ("RYG Red + Category Kanban", dict(ryg="R", cat="K")),
    ("RYG Red+Yellow + Category Forecast", dict(ryg="RY", cat="F")),
    ("Cards Aged 0 Days + RYG Green", dict(do="A0", ryg="G")),
    ("Cards Not cycled + RYG Red+Yellow", dict(do="ANC", ryg="RY")),
    ("Cards Aged > 5 Days + Category Kanban", dict(do="AP", cat="K")),
    ("Cards Aged 1 Days + Category Forecast", dict(do="A1", cat="F")),
    ("Cards Aged 2 Days + Category Kanban + RYG Green", dict(do="A2", cat="K", ryg="G")),
    ("Cards Not cycled + Category Forecast + RYG Red+Yellow+Green", dict(do="ANC", cat="F")),
    ("Show My Items List + RYG Green", dict(so="MI", ryg="G")),
    ("Show My Items List + Category Kanban", dict(so="MI", cat="K")),
    ("Show My Items List + Cards Aged 0 Days", dict(so="MI", do="A0")),
]
for name, kw in COMBOS:
    def f(kw=kw):
        r = run(**kw)
        problems = []
        if "ryg" in kw:
            allowed = set().union(*(RYG_IMG.get(c, set()) for c in kw["ryg"]))
            bad = {x.get("RYG_img") for x in r} - allowed
            if bad:
                problems.append(f"RYG filter not applied, unexpected indicators {sorted(bad)}")
        if kw.get("cat", "FK") != "FK":
            exp = items(SINGLE.get("cat" + kw["cat"], []))
            if items(r) - exp:
                problems.append(f"Category filter not applied, {len(items(r) - exp)} item(s) outside the category: {sorted(items(r) - exp)[:3]}")
        if kw.get("do", "$") != "$":
            exp = items(AGING_ROWS.get(kw["do"], []))
            if items(r) - exp:
                problems.append(f"Cards filter not applied, {len(items(r) - exp)} item(s) outside the aging bucket: {sorted(items(r) - exp)[:3]}")
        if kw.get("so") == "MI":
            exp = items(SINGLE.get("showMI", []))
            if items(r) - exp:
                problems.append(f"My Items filter not applied, {len(items(r) - exp)} extra item(s)")
        return not problems, f"{len(r)} rows. " + ("; ".join(problems) if problems else "All selected filters honoured")
    case("Filter Combination", name, "Select " + name + ", click Go.", "Result honours every selected filter (rows are within each single-filter result).", f)

# supplier combination

# ---------------------------------------------------------------- Persistence / reset behaviour
def f():
    set_filters(so="MI", ryg="G", cat="K")
    d.get(ITEMS_URL)
    wait_grid()
    shown = js("return [document.getElementById('FILTER_SO').value, [...document.getElementById('FILTER_RYG').selectedOptions].map(o=>o.value).join(''), [...document.getElementById('FILTER_CAT').selectedOptions].map(o=>o.value).join('')]")
    r = read_all()
    grid_green_only = {x.get("RYG_img") for x in r} <= RYG_IMG.get("G", set())
    ok = grid_green_only if shown[1] == "G" else True
    return ok, f"After reload dropdowns show Show={shown[0]}, RYG={shown[1]}, Category={shown[2]}; grid has {len(r)} rows (all Green: {grid_green_only})"
case("Filter - State", "Filter selections vs grid after page reload", "Set My Items List, Green, Kanban, click Go, reload page.",
     "Filter controls and grid show the same (saved) selection.", f)
load_default()

# ---------------------------------------------------------------- Search all columns
def search(text):
    js("var e=document.getElementById('ag-quick-filter');e.value=arguments[0];e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('keyup',{bubbles:true}))", text)
    time.sleep(1)
    return read_all()


def clear_search():
    search("")


for term, colk in (("IT_", "QKCItemNo"), ("test", "Description"), ("45", "TotalCardQty"), ("zzzzqq", None)):
    def f(term=term, colk=colk):
        r = search(term)
        if colk is None:
            return len(r) == 0, f"{len(r)} rows for non-matching text"
        miss = [x for x in r if term.lower() not in " ".join(str(v) for k, v in x.items() if not k.startswith("_")).lower()]
        full = [x for x in BASE_ROWS if term.lower() in " ".join(str(v) for k, v in x.items() if not k.startswith("_") and not k.endswith("_img")).lower()]
        return not miss and len(r) == len(full), f"{len(r)} rows, expected {len(full)}; rows without the text: {len(miss)}"
    case("Search all columns", f"Search '{term}'", f"Type '{term}' in Search all columns.", "Only rows containing the text in any column are listed.", f)
    clear_search()

# ---------------------------------------------------------------- Sorting
def header_click(col):
    d.find_element(By.CSS_SELECTOR, f".ag-header-cell[col-id='{col}'] .ag-header-cell-label").click()
    time.sleep(0.9)


def sort_state(col):
    return js("var h=document.querySelector(\".ag-header-cell[col-id='\"+arguments[0]+\"']\");return h?h.getAttribute('aria-sort'):null", col)


def check_order(col, rows, direction):
    vals = [x.get(col, "") for x in rows]
    if col == "RYG":
        seq = [x.get("RYG_img") for x in rows]
        groups = [k for k, _ in itertools.groupby(seq)]
        return len(groups) == len(set(groups)), f"colour groups in order: {groups}", False
    if col in NUMERIC:
        keys = [num(v) for v in vals]
        exp = sorted(keys, reverse=direction == "desc")
        return keys == exp, f"first values {vals[:4]} ... last {vals[-3:]}", False
    ci = lambda s: s.lower()
    alnum = lambda s: re.sub(r"[\W_]+", "", s.lower())
    rev = direction == "desc"

    def mono(key):
        ks = [key(v) for v in vals]
        return all((a >= b) if rev else (a <= b) for a, b in zip(ks, ks[1:]))

    def viol(key):
        for i, (a, b) in enumerate(zip(vals, vals[1:])):
            if (key(a) < key(b)) if rev else (key(a) > key(b)):
                return f"row {i + 1} '{a}' before row {i + 2} '{b}'"
        return "none"
    if mono(ci) or mono(alnum):
        return True, f"first {vals[:4]}", False
    if mono(lambda s: s):
        return False, f"first {vals[:5]}; order is case-sensitive (lowercase values after uppercase)", True
    return False, f"not in {direction}ending order; first violation: {viol(ci)}; first {vals[:4]}", False


for col in COLS:
    def f(col=col):
        js("document.getElementById('ag-quick-filter').value=''")
        load_default()
        res_ = []
        ok_all = True
        for step, direction in ((1, "asc"), (2, "desc")):
            header_click(col)
            st = sort_state(col)
            rows_ = read_all()
            ok, note, ci_only = check_order(col, rows_, "asc" if direction == "asc" else "desc")
            if st not in ({"asc": "ascending", "desc": "descending"}[direction],):
                ok = False
                note += f" | aria-sort='{st}' expected {direction}ending"
            if col == "RYG" and direction == "desc":
                pass
            if ci_only:
                side["case_sort"].append((col, direction))
                ok = False
                note += " | order is case-sensitive (lowercase after uppercase)"
            ok_all &= ok
            res_.append(f"{direction}: {'OK' if ok else 'WRONG'} ({note})")
        header_click(col)
        st = sort_state(col)
        rows_ = read_all()
        restored = [x.get("QKCItemNo") for x in rows_] == [x.get("QKCItemNo") for x in BASE_ROWS]
        res_.append(f"3rd click state={st}, original order restored={restored}")
        ok_all &= (st in (None, "none")) and restored
        return ok_all, " || ".join(res_)
    case("Sorting", f"Sort column '{LABEL[col]}' asc / desc / clear", f"Click '{LABEL[col]}' header three times; verify order across both pages.",
         "Ascending, descending, then original (unsorted) order; whole result set sorted, not just one page.", f)


def f():
    load_default()
    header_click("TotalCardQty")
    header_click("TotalCardQty")
    set_filters(ryg="G")
    st = sort_state("TotalCardQty")
    rows_ = read_all()
    ok, note, _ = check_order("TotalCardQty", rows_, "desc")
    return (st == "descending" and ok) or st in (None, "none"), f"Sorted by Total Qty desc, then RYG=Green applied: aria-sort={st}; {note}"
case("Sorting", "Sort after applying a filter with Go", "Sort Total Qty descending, select RYG=Green, Go.", "Grid is either still sorted descending with the indicator shown, or the indicator is cleared.", f)


def f():
    load_default()
    set_filters(ryg="G", cat="K")
    header_click("QKCItemNo")
    rows_ = read_all()
    ok, note, _ = check_order("QKCItemNo", rows_, "asc")
    return ok, f"Filtered ({len(rows_)} rows) + sorted by Item asc: {note}"
case("Sorting", "Sort a filtered result (Green + Kanban) by Item", "Apply RYG=Green, Category=Kanban, Go; sort by Item.", "Filtered rows are sorted correctly.", f)


def f():
    load_default()
    header_click("IsConsignmentItem")
    ActionChains(d).key_down(Keys.SHIFT).click(d.find_element(By.CSS_SELECTOR, ".ag-header-cell[col-id='TotalCardCount'] .ag-header-cell-label")).key_up(Keys.SHIFT).perform()
    time.sleep(0.9)
    rows_ = read_all()
    keys = [(x.get("IsConsignmentItem"), num(x.get("TotalCardCount"))) for x in rows_]
    return keys == sorted(keys), f"Multi-sort Is Consignment then Total Cards; first {keys[:3]}"
case("Sorting", "Multi-column sort with Shift+click", "Sort Is Consignment, Shift+click Total Cards.", "Rows ordered by Is Consignment then Total Cards.", f)

# ---------------------------------------------------------------- finish
load_default()
shot("final")
d.quit()

json.dump(dict(run=datetime.datetime.now().isoformat(), baseline=len(BASE_ROWS), results=results, side=side),
          open(os.path.join(HERE, OUT), "w", encoding="utf-8"), indent=1, default=list)
c = collections.Counter(r["status"] for r in results)
print("DONE", dict(c), flush=True)
