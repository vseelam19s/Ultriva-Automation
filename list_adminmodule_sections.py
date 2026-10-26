import requests, json

URL  = 'https://upland.testrail.com/'
AUTH = ('vseelam@uplandsoftware.com', 'LR5Bc8syGLl4d.dweMDC-bN9OoDA5pyiO6dKCHlh3')

r    = requests.get(URL + 'index.php?/api/v2/get_sections/15&suite_id=2571',
                    headers={'Content-Type': 'application/json'}, auth=AUTH)
secs = r.json().get('sections', r.json())

id_map = {s['id']: s for s in secs}

def path(sid):
    s = id_map.get(sid, {})
    p = s.get('parent_id')
    return (path(p) + ' > ' if p else '') + s.get('name', '?')

print(f"{'ID':>8}  Section Path")
print('-' * 70)
for s in sorted(secs, key=lambda x: path(x['id'])):
    print(f"  {s['id']:>8}  {path(s['id'])}")
