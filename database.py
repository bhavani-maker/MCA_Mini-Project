import sqlite3
from datetime import datetime

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('agricultural_rental.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            user_type TEXT NOT NULL,
            phone TEXT,
            location TEXT,
            farm_size TEXT,
            crops TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Equipment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'General',
            cost_per_day INTEGER NOT NULL,
            price_per_hour INTEGER NOT NULL,
            suitable_for TEXT NOT NULL,
            land_min REAL NOT NULL,
            available BOOLEAN DEFAULT 1,
            image TEXT,
            description TEXT,
            owner_id INTEGER,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')
    
    # Bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT UNIQUE NOT NULL,
            equipment_name TEXT NOT NULL,
            farmer_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            rental_duration INTEGER NOT NULL,
            hourly_rate INTEGER NOT NULL,
            total_amount INTEGER NOT NULL,
            payment_method TEXT DEFAULT 'COD',
            payment_status TEXT DEFAULT 'PENDING',
            booking_status TEXT DEFAULT 'CONFIRMED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farmer_id) REFERENCES users (id)
        )
    ''')
    
    # Insert default admin user
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, name, user_type)
        VALUES ('admin', 'admin123', 'Administrator', 'admin')
    ''')
    
    # Insert sample owner user
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, name, user_type, location)
        VALUES ('owner1', 'owner123', 'Sample Owner', 'owner', 'Maharashtra')
    ''')
    
    # Get owner ID
    owner_id = cursor.execute('SELECT id FROM users WHERE username = "owner1"').fetchone()[0]
    
    # Insert default equipment
    equipment_data = [
        ('Heavy Duty Tractor', 'Tractor', 1500, 200, 'ploughing,sowing', 2, 1, 'tractor.jpg', 'Heavy duty tractor for large farms', owner_id, 'Mumbai, Maharashtra'),
        ('Mini Tractor', 'Tractor', 800, 100, 'sowing,cultivation', 1, 1, 'mini_tractor.jpg', 'Compact tractor for small farms', owner_id, 'Pune, Maharashtra'),
        ('Combine Harvester', 'Harvester', 2000, 250, 'harvesting', 3, 1, 'harvester.jpg', 'Efficient harvesting machine', owner_id, 'Nashik, Maharashtra'),
        ('Crop Sprayer', 'Sprayer', 600, 80, 'irrigation,spraying', 0.5, 1, 'sprayer.jpg', 'Pesticide and fertilizer spraying', owner_id, 'Kolhapur, Maharashtra'),
        ('Cultivator', 'Cultivator', 1000, 130, 'ploughing,cultivation', 1, 1, 'cultivator.jpg', 'Soil preparation equipment', owner_id, 'Solapur, Maharashtra'),
        ('Thresher Machine', 'Harvester', 1200, 150, 'harvesting,threshing', 2, 1, 'thresher.jpg', 'Grain separation machine', owner_id, 'Aurangabad, Maharashtra')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO equipment (name, type, cost_per_day, price_per_hour, suitable_for, land_min, available, image, description, owner_id, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', equipment_data)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()