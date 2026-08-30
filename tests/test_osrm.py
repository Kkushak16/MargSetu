import urllib.request
import json

url = 'https://router.project-osrm.org/route/v1/driving/88.3953,26.7271;88.6065,27.3389?overview=full&geometries=geojson'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        coords = data['routes'][0]['geometry']['coordinates']
        print(f"Success! Got {len(coords)} exact road coordinates along NH10!")
        print("First 3 points:", coords[:3])
        print("Last 3 points:", coords[-3:])
except Exception as e:
    print("Error:", e)
