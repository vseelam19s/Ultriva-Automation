import requests, json
URL="https://upland.testrail.com/"
AUTH=("vseelam@uplandsoftware.com","LR5Bc8syGLl4d.dweMDC-bN9OoDA5pyiO6dKCHlh3")
HEADERS={"Content-Type":"application/json"}
PROJECT_ID=15
SUITE_ID=2571
resp = requests.get(URL+"index.php?/api/v2/get_sections/"+str(PROJECT_ID)+"&suite_id="+str(SUITE_ID), headers=HEADERS, auth=AUTH)
data = resp.json()
sections = data if isinstance(data, list) else data.get("sections", [])
for s in sections:
    name = s.get("name","")
    if "item" in name.lower():
        print(f"ID={s['id']}  parent={s.get('parent_id')}  name={name}")
print("--- All sections ---")
for s in sections:
    print(f"ID={s['id']}  parent={s.get('parent_id')}  name={s.get('name')}")
