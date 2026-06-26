import os
import json

# Booking and payment management functions
def load_bookings():
    if os.path.exists('bookings.json'):
        with open('bookings.json', 'r') as f:
            return json.load(f)
    return {}

def save_bookings(bookings):
    with open('bookings.json', 'w') as f:
        json.dump(bookings, f, indent=2)

def get_equipment_price(equipment_name):
    """Get hourly price for equipment"""
    equipment_map = {
        'tractor': 200,
        'mini tractor': 200,
        'seed drill': 100,
        'harvester': 250,
        'sprayer': 80,
        'cultivator': 130,
        'thresher': 150
    }
    return equipment_map.get(equipment_name.lower(), 150)