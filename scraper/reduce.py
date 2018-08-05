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
        'location': {
            'lat': place['location']['latitude'],
            'long': place['location']['longitude']
        },
        'name': place['name'],
        'offer': place['offer_type'],
        'rating': place['user_rating']['aggregate_rating'],
        'deeplink': place['deeplink'],
        'cost': place['average_cost_for_two'],
        'cuisines': place['cuisines']
    })

Path('src/places.json').write_text(json.dumps(reduced_places, indent=4, sort_keys=True))