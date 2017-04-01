import json
import os
import os
here = os.path.dirname(os.path.realpath(__file__))

# TODO: move to lib or tools
with open(os.path.join(here, 'Province.json')) as f:
    tmp = json.load(f)
    province = [i['name'].strip() for i in tmp]
    cities = {i['name']: [j['name'] for j in i['Cities']] for i in tmp}
