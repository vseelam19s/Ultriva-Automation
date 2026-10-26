from lib import *
d = make_driver()
login(d); open_list(d)
select_plant(d, PLANTS["Cust1201023"])
for _ in range(3):
    st = sort_state(d)
    if all(v in (None, "none") for v in st.values()):
        break
    for c, v in st.items():
        if v in ("ascending", "descending"):
            click_header(d, c); break
click_header(d, "PlantItemNo")
time.sleep(1)
d.save_screenshot("shots/case_sort_PlantItemNo.png")
print([r["PlantItemNo"] for r in rows(d)])
d.quit()
