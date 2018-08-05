from pathlib import Path
import json
import datetime

raw_places = json.loads(Path('zomato_places.json').read_text())

reduced_places = {
    'updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'places': []
}

for place in raw_places:
    reduced_places['places'].append({
        ''
    })

Path('src/places.json').write_text(json.dumps(reduced_places))