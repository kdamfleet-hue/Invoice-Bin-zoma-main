import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services import gps_history as gh

store = {}

def get(key):
    return store.get(key)

def put(key, value):
    store[key] = value

gh._global_blob_get = get
gh._global_blob_set = put

vehicles = [{
    'id': 7, 'name': 'اختبار مركبة', 'plate': 'TEST-7', 'driver': '',
    'lat': 26.42, 'lng': 50.09, 'speed_kmh': 40, 'status': 'moving',
    'heading': 90, 'odometer_km': 10,
}]
assert gh.record_snapshot(vehicles, '2026-09-05T00:00:00+00:00') == 1
assert gh.record_snapshot(vehicles, '2026-09-05T00:00:10+00:00') == 0
assert len(gh.get_history('7')) == 1

fence = gh.save_geofence({'name': 'الساحة', 'lat': 26.42, 'lng': 50.09, 'radius_m': 250})
assert fence['name'] == 'الساحة'
result = gh.evaluate_geofences(vehicles)
assert result['events'] and result['events'][0]['event'] == 'entry'
assert gh.delete_geofence(fence['id']) is True
try:
    gh.save_geofence({'name': '', 'lat': 26.42, 'lng': 50.09, 'radius_m': 250})
except ValueError:
    pass
else:
    raise AssertionError('invalid geofence accepted')
print('gps advanced service tests: ok')
