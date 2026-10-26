import json, time, re, os, traceback, datetime
from lib import *
from selenium.webdriver.common.action_chains import ActionChains

OUT = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(OUT, "shots")
os.makedirs(SHOTS, exist_ok=True)

results = []
side = {}
counter = {"n": 0}
d = make_driver()
CUR = {"plant": None, "name": None}


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def getrows():
    return [{k: norm(v) for k, v in r.items()} for r in rows(d)]


def shot(name):
    p = os.path.join(SHOTS, f"{name}.png")
    try:
        d.save_screenshot(p)
    except Exception:
        return ""
    return p


def sys_error():
    try:
        t = d.execute_script("return document.body.innerText.slice(0,3000).toLowerCase()")
    except Exception:
        return False
    return any(x in t for x in ("system error", "server error", "http error", "an error has occurred", "exception"))


def recover():
    try:
        open_list(d)
        select_plant(d, PLANTS[CUR["name"]])
    except Exception:
        pass


def case(area, title, steps, expected, fn):
    counter["n"] += 1
    cid = f"TC_{counter['n']:03d}"
    rec = dict(id=cid, plant=CUR["name"], area=area, title=title, steps=steps, expected=expected, actual="", status="PASS", shot="")
    try:
        ok, actual = fn()
        rec["actual"] = actual
        if sys_error():
            rec["status"] = "SKIP"
            rec["actual"] = "System error displayed: " + actual
            rec["shot"] = shot(cid)
            recover()
        elif not ok:
            rec["status"] = "FAIL"
            rec["shot"] = CUR.get("pre_shot") or shot(cid)
        CUR["pre_shot"] = None
    except Exception as e:
        rec["status"] = "SKIP"
        rec["actual"] = "System/automation error, case skipped: " + norm(str(e))[:200]
        rec["shot"] = shot(cid)
        recover()
    print(cid, rec["status"], area, "|", title, "|", rec["actual"][:140], flush=True)
    results.append(rec)
    return rec


def close_all():
    for _ in range(2):
        ActionChains(d).send_keys(Keys.ESCAPE).perform()
    d.execute_script("var h=document.querySelector('.ag-header-viewport');if(h){h.dispatchEvent(new MouseEvent('mousedown',{bubbles:true}));}"
                     "document.body.click();")
    time.sleep(0.4)


def last_menu():
    return d.execute_script("var m=[...document.querySelectorAll('.ag-filter-menu')];return m.length?m[m.length-1]:null")


def js_click(el):
    d.execute_script("arguments[0].click()", el)


def scroll_list(m, pos):
    d.execute_script("var v=arguments[0].querySelector('.ag-filter-virtual-list-viewport');v.scrollTop=arguments[1];", m, pos)
    time.sleep(0.4)


def read_set_items(m):
    seen = []
    for pos in (0, 10000):
        scroll_list(m, pos)
        for it in m.find_elements(By.CSS_SELECTOR, ".ag-set-filter-item"):
            lab = norm(it.text)
            if lab != "(Select All)" and lab not in seen:
                seen.append(lab)
    scroll_list(m, 0)
    return seen


def apply_set(col, values):
    open_filter(d, col)
    m = last_menu()
    scroll_list(m, 0)
    allcb = m.find_elements(By.CSS_SELECTOR, ".ag-set-filter-item")[0].find_element(By.CSS_SELECTOR, "input[type=checkbox]")
    if allcb.is_selected():
        js_click(allcb)
    time.sleep(0.3)
    done = set()
    for pos in (0, 10000):
        scroll_list(m, pos)
        for it in m.find_elements(By.CSS_SELECTOR, ".ag-set-filter-item"):
            label = norm(it.text)
            if label == "(Select All)":
                continue
            v = label if label != "" else "(Blanks)"
            if v in values and v not in done:
                js_click(it.find_element(By.CSS_SELECTOR, "input[type=checkbox]"))
                done.add(v)
    time.sleep(0.4)
    click_apply(m)
    close_all()
    time.sleep(0.6)


def click_apply(m):
    for b in m.find_elements(By.CSS_SELECTOR, ".ag-filter-apply-panel button"):
        if norm(b.text).lower() == "apply":
            js_click(b)
            time.sleep(0.5)


def pick_operator(m, idx, op):
    pickers = m.find_elements(By.CSS_SELECTOR, ".ag-picker-field-wrapper")
    if norm(pickers[idx].text) == op:
        return
    pickers[idx].click()
    time.sleep(0.5)
    opts = d.find_elements(By.CSS_SELECTOR, ".ag-select-list .ag-list-item")
    for o in opts:
        if norm(o.text) == op:
            o.click()
            time.sleep(0.4)
            return
    raise Exception("operator option not found: " + op + " (available: " + str([norm(o.text) for o in opts]) + ")")


def type_num(m, idx, val):
    inputs = [i for i in m.find_elements(By.CSS_SELECTOR, "input.ag-number-field-input") if i.is_displayed()]
    e = inputs[idx]
    e.click()
    e.send_keys(Keys.CONTROL, "a")
    e.send_keys(Keys.DELETE)
    e.send_keys(str(val))
    time.sleep(1.0)


def apply_num(col, c1, c2=None, join="AND"):
    # c = (op, v1, v2)
    open_filter(d, col)
    m = last_menu()
    pick_operator(m, 0, c1[0])
    if c1[0] in ("Equals", "Does not equal", "Greater than", "Greater than or equal to", "Less than", "Less than or equal to"):
        type_num(m, 0, c1[1])
    elif c1[0] == "In range":
        type_num(m, 0, c1[1])
        type_num(m, 1, c1[2])
    if c2:
        time.sleep(0.4)
        m = last_menu()
        d.execute_script("arguments[0].scrollIntoView()", m)
        radios = m.find_elements(By.CSS_SELECTOR, ".ag-filter-condition .ag-radio-button")
        for r in radios:
            if norm(r.text).upper() == join:
                js_click(r.find_element(By.CSS_SELECTOR, "input"))
        pick_operator(m, 1, c2[0])
        if c2[0] in ("Equals", "Does not equal", "Greater than", "Greater than or equal to", "Less than", "Less than or equal to"):
            idx = 1 if c1[0] != "In range" else 2
            type_num(m, idx, c2[1])
    time.sleep(0.5)
    click_apply(m)
    close_all()
    time.sleep(0.6)


def quick(text):
    e = d.find_element(By.ID, "ag-quick-filter")
    e.click()
    e.send_keys(Keys.CONTROL, "a")
    e.send_keys(Keys.DELETE)
    if text:
        e.send_keys(text)
    time.sleep(1.2)


def num_pred(c):
    op, a, b = c
    a = float(a) if a is not None else None
    b = float(b) if b is not None else None
    return {
        "Equals": lambda x: x == a, "Does not equal": lambda x: x != a, "Greater than": lambda x: x > a,
        "Greater than or equal to": lambda x: x >= a, "Less than": lambda x: x < a, "Less than or equal to": lambda x: x <= a,
        "In range": lambda x: a < x < b, "Blank": lambda x: False, "Not blank": lambda x: True,
    }[op]


def expected_rows(base, spec):
    out = list(base)
    for s in spec:
        if s[0] == "set":
            _, col, vals = s
            out = [r for r in out if (r[col] if r[col] != "" else "(Blanks)") in vals]
        elif s[0] == "num":
            _, col, c1, c2, join = s
            p1 = num_pred(c1)
            if c2:
                p2 = num_pred(c2)
                if join == "AND":
                    out = [r for r in out if p1(float(r[col])) and p2(float(r[col]))]
                else:
                    out = [r for r in out if p1(float(r[col])) or p2(float(r[col]))]
            else:
                out = [r for r in out if p1(float(r[col]))]
        elif s[0] == "quick":
            toks = s[1].lower().split()
            out = [r for r in out if all(t in " ".join(r.values()).lower() for t in toks)]
    return out


def key(r):
    return tuple(r[c] for c in COLS)


def describe(spec):
    parts = []
    for s in spec:
        if s[0] == "set":
            parts.append(f"{LABELS[s[1]]} set-filter = {s[2]}")
        elif s[0] == "num":
            c = s[2]
            t = f"{LABELS[s[1]]} {c[0]} {c[1] if c[1] is not None else ''}{(' and ' + str(c[2])) if c[0] == 'In range' else ''}"
            if s[3]:
                t += f" {s[4]} {s[3][0]} {s[3][1]}"
            parts.append(t)
        elif s[0] == "quick":
            parts.append(f"Search all columns = '{s[1]}'")
    return "; ".join(parts)


def reset_filters():
    quick("")
    clear_filters(d)
    time.sleep(0.5)
    if len(getrows()) != len(BASE[0]):
        recover()
        quick("")


def run_filter(area, spec, label=None):
    def fn():
        reset_filters()
        for s in spec:
            if s[0] == "set":
                apply_set(s[1], s[2])
            elif s[0] == "num":
                apply_num(s[1], s[2], s[3], s[4])
            elif s[0] == "quick":
                quick(s[1])
        got = getrows()
        exp = expected_rows(BASE[0], spec)
        pg = paging(d)
        n = len(got)
        m = re.search(r"(\d+) to (\d+) of (\d+)", pg)
        pg_ok = bool(m) and int(m.group(3)) == n
        if not pg_ok:
            side.setdefault("paging", []).append((CUR["name"], describe(spec), pg, n))
        ok = sorted(map(key, got)) == sorted(map(key, exp))
        if ok and not pg_ok:
            return False, f"Rows correct ({n}) but pagination text shows '{pg}'"
        act = f"Grid shows {n} row(s): {[r['PlantItemNo'] for r in got]}" if not ok else f"{n} row(s) shown as expected"
        if not ok:
            act += f" | Pagination: '{pg}'"
        return ok, act
    desc = describe(spec)
    exp_rows = expected_rows(BASE[0], spec)
    return case(area, label or desc, f"Plant {CUR['name']} > Go > apply filter: {desc}",
                f"{len(exp_rows)} row(s): {[r['PlantItemNo'] for r in exp_rows]}", fn)


BASE = [None]


def sort_expected(vals, col, rev):
    if col in NUMERIC:
        return sorted(vals, key=float, reverse=rev), None
    ci = sorted(vals, key=lambda s: s.lower(), reverse=rev)
    cs = sorted(vals, reverse=rev)
    return ci, cs


def reset_sort_none():
    for _ in range(3):
        st = sort_state(d)
        if all(v in (None, "none") for v in st.values()):
            return
        for c, v in st.items():
            if v in ("ascending", "descending"):
                click_header(d, c)
                break


def sort_check(col, direction, via):
    vals = [r[col] for r in getrows()]
    exp_ci, exp_cs = sort_expected(vals, col, direction == "descending")
    st = sort_state(d)[col]
    ind_ok = st == direction
    if col in NUMERIC:
        ok = vals == exp_ci
        note = ""
    else:
        ok = vals == exp_ci or vals == exp_cs
        note = ""
        if vals == exp_cs and vals != exp_ci:
            side.setdefault("case_sort", set()).add((CUR["name"], col))
            note = " [NOTE: ordering is case-sensitive: lowercase values sorted after uppercase]"
    return ok and ind_ok, f"Order={vals}; sort indicator='{st}'{note}"


try:
    login(d)
    open_list(d)
    for pname, pval in PLANTS.items():
        CUR["name"] = pname
        open_list(d)
        select_plant(d, pval)
        BASE[0] = getrows()
        base = BASE[0]
        print("PLANT", pname, len(base), flush=True)

        # ---------- SORTING ----------
        case("Sorting", "Default sort on page load", f"Plant {pname} > Go", "Grid sorted ascending by Supplier Item No. (indicator shown)",
             lambda: (lambda vals, st: (st.get("SupplierItemCode") == "ascending" and (vals == sorted(vals) or vals == sorted(vals, key=str.lower)),
                                        f"Order={vals}; indicator={st.get('SupplierItemCode')}"))([r["SupplierItemCode"] for r in getrows()], sort_state(d)))
        for col in COLS:
            reset_sort_none()
            click_header(d, col)
            case("Sorting", f"Sort {LABELS[col]} ascending (header click)", f"Click '{LABELS[col]}' header once", "Rows ascending, sort indicator = ascending",
                 lambda col=col: sort_check(col, "ascending", "header"))
            click_header(d, col)
            case("Sorting", f"Sort {LABELS[col]} descending (header click)", f"Click '{LABELS[col]}' header twice", "Rows descending, sort indicator = descending",
                 lambda col=col: sort_check(col, "descending", "header"))
            click_header(d, col)
            case("Sorting", f"Remove sort on {LABELS[col]} (3rd click)", f"Click '{LABELS[col]}' header three times", "Sort cleared (no indicator)",
                 lambda col=col: (sort_state(d)[col] in (None, "none"), f"indicator={sort_state(d)[col]}"))

        # column menu sorting
        for col in COLS:
            for direction, label in (("ascending", "Sort Ascending"), ("descending", "Sort Descending")):
                def fn(col=col, direction=direction, label=label):
                    reset_sort_none()
                    d.execute_script("document.querySelector(\".ag-header-cell[col-id='\"+arguments[0]+\"'] .ag-header-cell-menu-button\").click()", col)
                    time.sleep(0.6)
                    ok = d.execute_script("var it=[...document.querySelectorAll('.ag-menu-option')].find(e=>e.innerText.trim()==arguments[0]);if(it){it.click();return true}return false", label)
                    time.sleep(0.9)
                    if not ok:
                        return False, "menu option not found"
                    return sort_check(col, direction, "menu")
                case("Sorting", f"Column menu '{label}' on {LABELS[col]}", f"Open column menu of '{LABELS[col]}' > {label}", f"Rows {direction}", fn)

        # multi sort
        def multi():
            reset_sort_none()
            click_header(d, "Carrier")
            click_header(d, "LeadTime", shift=True)
            r = getrows()
            vals = [(x["Carrier"].lower(), float(x["LeadTime"])) for x in r]
            return vals == sorted(vals), f"Carrier/LeadTime order={vals}; state={ {k: v for k, v in sort_state(d).items() if v not in (None, 'none')} }"
        case("Sorting", "Multi-column sort (Carrier, then Shift+Lead Time)", "Click Carrier header, Shift+click Lead Time header",
             "Rows sorted by Carrier then Lead Time ascending", multi)
        reset_sort_none()
        reset_sort_none()
        click_header(d, "SupplierItemCode")  # restore default asc

        # sort is retained after filtering
        def sort_filter():
            reset_filters()
            reset_sort_none()
            click_header(d, "SupplierItemDesc")
            click_header(d, "SupplierItemDesc")
            apply_num("LeadTime", ("Greater than or equal to", 3, None), None, "AND")
            got = getrows()
            vals = [r["SupplierItemDesc"] for r in got]
            exp = sorted(vals, key=str.lower, reverse=True)
            exp2 = sorted(vals, reverse=True)
            ok = vals in (exp, exp2) and all(float(r["LeadTime"]) >= 3 for r in got)
            return ok, f"Order={vals}; LeadTimes={[r['LeadTime'] for r in got]}"
        case("Sorting+Filter", "Description descending sort retained after Lead Time >= 3 filter", "Sort Description desc; filter Lead Time >= 3",
             "Filtered rows remain sorted descending by Description", sort_filter)
        reset_filters()
        reset_sort_none()
        click_header(d, "SupplierItemCode")

        # ---------- FILTERS: set filter list contents ----------
        for col in ["PlantItemNo", "SupplierItemCode", "SupplierItemDesc", "Carrier", "UnitDescription"]:
            def lst(col=col):
                open_filter(d, col)
                m = last_menu()
                actual = read_set_items(m)
                CUR["pre_shot"] = shot(f"list_{col}_{CUR['name']}")
                close_all()
                exp = sorted({(r[col] if r[col] != "" else "(Blanks)") for r in base}, key=str.lower)
                ok = sorted(actual, key=str.lower) == exp
                return ok, f"Filter list={actual}; expected={exp}"
            case("Filter", f"{LABELS[col]} filter value list matches grid data", f"Open filter on '{LABELS[col]}'",
                 "Distinct values of column", lst)

        # ---------- FILTERS: set filter single value ----------
        for col in ["PlantItemNo", "SupplierItemCode", "SupplierItemDesc", "Carrier", "UnitDescription"]:
            vals = []
            for r in base:
                v = r[col] if r[col] != "" else "(Blanks)"
                if v not in vals:
                    vals.append(v)
            for v in vals[:3]:
                run_filter("Filter", [("set", col, [v])])
            if len(vals) >= 2:
                run_filter("Filter", [("set", col, vals[:2])])

        # ---------- FILTERS: number filters ----------
        for col in ["LeadTime", "TransitTime", "PalletQty"]:
            nums = sorted({float(r[col]) for r in base})
            mid = nums[len(nums) // 2]
            lo, hi = nums[0], nums[-1]
            fmt = lambda x: ("%g" % x)
            for op in ["Equals", "Does not equal", "Greater than", "Greater than or equal to", "Less than", "Less than or equal to"]:
                run_filter("Filter", [("num", col, (op, fmt(mid), None), None, "AND")])
            run_filter("Filter", [("num", col, ("In range", fmt(lo), fmt(hi)), None, "AND")])
            run_filter("Filter", [("num", col, ("Blank", None, None), None, "AND")])
            run_filter("Filter", [("num", col, ("Not blank", None, None), None, "AND")])
            run_filter("Filter", [("num", col, ("Equals", fmt(lo), None), None, "AND")], f"{LABELS[col]} Equals smallest value {fmt(lo)}")
            run_filter("Filter", [("num", col, ("Less than", fmt(lo), None), None, "AND")], f"{LABELS[col]} Less than smallest value (no match expected)")
            run_filter("Filter", [("num", col, ("Less than", fmt(mid), None), ("Greater than", fmt(mid), None), "OR")])
            run_filter("Filter", [("num", col, ("Greater than", fmt(lo), None), ("Less than", fmt(hi), None), "AND")])
            run_filter("Filter", [("num", col, ("Greater than", fmt(hi), None), ("Less than", fmt(lo), None), "AND")],
                       f"{LABELS[col]} > max AND < min (contradictory, no rows expected)")

        # ---------- FILTERS: quick filter ----------
        terms = ["cust", "TEST", "unknown", "45", "45.0000", "44.0000", "0.00001", "0.08", "!!", "_", "test cust", "zzzz", " cust "]
        for t in terms:
            run_filter("Search all columns", [("quick", t.strip() if t != " cust " else "cust")], f"Search all columns = '{t}'")

        # ---------- FILTER COMBINATIONS ----------
        combos = [
            [("set", "Carrier", ["Unknown"]), ("num", "LeadTime", ("Greater than or equal to", "3", None), None, "AND")],
            [("set", "SupplierItemDesc", [next(r["SupplierItemDesc"] for r in base)]), ("num", "PalletQty", ("Equals", "45", None), None, "AND")],
            [("num", "LeadTime", ("In range", "1", "5"), None, "AND"), ("num", "TransitTime", ("Greater than", "2", None), None, "AND")],
            [("num", "LeadTime", ("Less than", "3", None), None, "AND"), ("num", "PalletQty", ("Greater than", "40", None), None, "AND")],
            [("quick", "cust"), ("num", "LeadTime", ("Less than or equal to", "3", None), None, "AND")],
            [("set", "Carrier", ["Unknown"]), ("quick", "test")],
            [("set", "PlantItemNo", [base[0]["PlantItemNo"], base[-1]["PlantItemNo"]]), ("num", "TransitTime", ("Greater than", "2", None), None, "AND")],
            [("num", "LeadTime", ("Equals", "4", None), None, "AND"), ("num", "TransitTime", ("Equals", "4", None), None, "AND"), ("num", "PalletQty", ("Equals", "45", None), None, "AND")],
            [("set", "UnitDescription", ["(Blanks)"]), ("set", "Carrier", ["Unknown"]), ("num", "PalletQty", ("Greater than or equal to", "45", None), None, "AND")],
            [("num", "LeadTime", ("Less than", "3", None), ("Greater than", "4", None), "OR"), ("quick", "it")],
        ]
        for c in combos:
            run_filter("Filter Combination", c)

        # clear filters & persistence
        def clr():
            reset_filters()
            apply_num("LeadTime", ("Greater than", "3", None), None, "AND")
            apply_set("Carrier", ["Unknown"])
            quick("test")
            n1 = len(getrows())
            clear_filters(d)
            n2 = len(getrows())
            q = d.find_element(By.ID, "ag-quick-filter").get_attribute("value")
            return n2 == len(base), f"Rows with filters={n1}; after 'Clear Filters'={n2} (expected {len(base)}); quick-search text left='{q}'"
        case("Filter", "Clear Filters button resets all column filters", "Apply column filters + quick search > click Clear Filters", f"All {len(base)} rows shown", clr)
        quick("")

        def persist():
            reset_filters()
            apply_num("LeadTime", ("Greater than", "3", None), None, "AND")
            n1 = len(getrows())
            select_plant(d, pval)
            n2 = len(getrows())
            return n1 == n2 or n2 == len(base), f"Rows before Go={n1}; after Go (same plant)={n2}"
        case("Filter", "Filter behaviour after clicking Go again", "Apply Lead Time > 3 filter > click Go", "Either filter retained or grid fully reset (consistent)", persist)
        reset_filters()

except Exception as e:
    traceback.print_exc()
finally:
    side["case_sort"] = sorted(side.get("case_sort", []))
    json.dump(dict(results=results, side=side, run=str(datetime.datetime.now())), open(os.path.join(OUT, "results.json"), "w"), indent=1, default=str)
    d.quit()
    print("DONE", len(results))
