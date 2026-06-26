"""
ML-Based Demand Prediction for Krushi Rent AI
Trains model ONCE on startup, caches result for instant predictions.
"""

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

DB_PATH = 'krushi_rent_ai.db'

BASE_DEMAND = {
    'Tractor': 8, 'Harvester': 6, 'Seeder': 5, 'Sprayer': 5,
    'Cultivator': 4, 'Irrigation': 4, 'Pump': 4, 'Weeder': 3,
    'Planter': 4, 'Mower': 3, 'Loader': 3, 'Trailer': 3,
    'Leveler': 3, 'Mulcher': 3, 'Chopper': 3,
}
DEFAULT_BASE = 4

SEASONAL_WEIGHTS = {
    'Tractor':    [0.8, 0.7, 1.0, 1.2, 1.1, 1.3, 1.5, 1.4, 1.2, 1.0, 0.9, 0.8],
    'Harvester':  [0.5, 0.5, 0.6, 0.7, 0.8, 1.0, 1.5, 1.8, 2.0, 1.5, 0.8, 0.6],
    'Seeder':     [0.6, 0.7, 1.0, 1.2, 1.0, 1.5, 1.8, 1.5, 1.0, 0.8, 0.7, 0.6],
    'Sprayer':    [0.7, 0.7, 0.8, 1.0, 1.2, 1.5, 1.8, 1.6, 1.3, 1.0, 0.8, 0.7],
    'Cultivator': [0.8, 0.8, 1.0, 1.2, 1.1, 1.3, 1.4, 1.3, 1.1, 1.0, 0.9, 0.8],
}
DEFAULT_SEASONAL = [0.8, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8]

# ── In-memory cache ──────────────────────────────────────────────
_cache = {
    'model': None,
    'le': None,
    'df': None,
    'summary': None,
    'trained_at': None,
}
CACHE_TTL_SECONDS = 300  # refresh every 5 minutes


def _cache_valid():
    if _cache['trained_at'] is None:
        return False
    return (datetime.now() - _cache['trained_at']).total_seconds() < CACHE_TTL_SECONDS


def _get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def _load_and_train():
    """Load data + train model once, store in cache."""
    conn = _get_db()
    try:
        df = pd.read_sql_query('''
            SELECT b.booking_date, b.duration_hours, b.total_amount,
                   e.type as equipment_type, e.price_per_day
            FROM bookings b
            JOIN equipment e ON b.equipment_id = e.id
            WHERE b.booking_date IS NOT NULL
        ''', conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()

    model, le = None, None

    if not df.empty and len(df) >= 5:
        df['booking_date'] = pd.to_datetime(df['booking_date'], errors='coerce')
        df = df.dropna(subset=['booking_date'])
        df['month']       = df['booking_date'].dt.month
        df['day_of_week'] = df['booking_date'].dt.dayofweek
        df['week_of_year']= df['booking_date'].dt.isocalendar().week.astype(int)
        df['is_weekend']  = (df['day_of_week'] >= 5).astype(int)

        le = LabelEncoder()
        all_types = list(BASE_DEMAND.keys()) + df['equipment_type'].fillna('Unknown').tolist()
        le.fit(all_types)
        df['type_enc'] = le.transform(
            df['equipment_type'].fillna('Unknown').apply(
                lambda x: x if x in le.classes_ else 'Unknown'
            )
        )

        X = df[['month','day_of_week','week_of_year','is_weekend','type_enc','price_per_day']].fillna(0)
        y = df['duration_hours'].fillna(8)

        model = RandomForestRegressor(n_estimators=30, max_depth=5,
                                      random_state=42, n_jobs=-1)
        model.fit(X, y)

    _cache['model'] = model
    _cache['le']    = le
    _cache['df']    = df
    _cache['trained_at'] = datetime.now()


def _demand_level(v):
    return 'High' if v >= 7 else 'Medium' if v >= 4 else 'Low'


def _predict_single(equipment_type, future_date, avg_price):
    """Predict bookings for one equipment type on one date (uses cache)."""
    month = future_date.month
    dow   = future_date.weekday()
    woy   = future_date.isocalendar()[1]
    is_we = int(dow >= 5)

    base     = BASE_DEMAND.get(equipment_type, DEFAULT_BASE)
    seasonal = SEASONAL_WEIGHTS.get(equipment_type, DEFAULT_SEASONAL)

    model = _cache['model']
    le    = _cache['le']

    if model is not None and le is not None:
        try:
            eq_type = equipment_type if equipment_type in le.classes_ else 'Unknown'
            type_enc = int(le.transform([eq_type])[0])
            feat = np.array([[month, dow, woy, is_we, type_enc, avg_price]])
            ml_factor = float(model.predict(feat)[0]) / 8.0
            return base * seasonal[month - 1] * ml_factor
        except Exception:
            pass

    pred = base * seasonal[month - 1]
    return pred * 1.2 if is_we else pred


def predict_demand_for_equipment(equipment_type, days_ahead=30):
    """Instant prediction using cached model."""
    if not _cache_valid():
        _load_and_train()

    df = _cache['df']
    today = datetime.today()

    eq_df = df[df['equipment_type'] == equipment_type] if (df is not None and not df.empty) else pd.DataFrame()
    avg_price = float(eq_df['price_per_day'].mean()) if not eq_df.empty else 1000.0
    if np.isnan(avg_price):
        avg_price = 1000.0

    predictions = []
    for i in range(days_ahead):
        future_date = today + timedelta(days=i + 1)
        pred = _predict_single(equipment_type, future_date, avg_price)
        predictions.append({
            'date': future_date.strftime('%Y-%m-%d'),
            'day':  future_date.strftime('%a'),
            'predicted_bookings': round(max(pred, 0.5), 1),
            'demand_level': _demand_level(pred)
        })
    return predictions


def get_demand_summary():
    """Instant summary using cached model — trains only once per TTL."""
    if not _cache_valid():
        _load_and_train()

    # Return cached summary if still valid
    if _cache['summary'] is not None and _cache_valid():
        return _cache['summary']

    df = _cache['df']

    conn = _get_db()
    try:
        rows = conn.execute('SELECT DISTINCT type FROM equipment WHERE available=1').fetchall()
        types = [r['type'] for r in rows] if rows else list(BASE_DEMAND.keys())
    except Exception:
        types = list(BASE_DEMAND.keys())
    finally:
        conn.close()

    summary = []
    for eq_type in types:
        preds = predict_demand_for_equipment(eq_type, days_ahead=7)
        vals  = [p['predicted_bookings'] for p in preds]
        avg   = round(sum(vals) / len(vals), 1)
        peak  = max(preds, key=lambda x: x['predicted_bookings'])

        hist = 0
        if df is not None and not df.empty:
            hist = int((df['equipment_type'] == eq_type).sum())

        trend = 'Stable'
        if len(vals) >= 6:
            a, b = sum(vals[:3]) / 3, sum(vals[4:]) / 3
            trend = 'Rising' if b > a * 1.1 else 'Falling' if b < a * 0.9 else 'Stable'

        summary.append({
            'equipment_type':     eq_type,
            'avg_daily_bookings': avg,
            'peak_day':           peak['date'],
            'peak_bookings':      peak['predicted_bookings'],
            'demand_level':       _demand_level(avg),
            'trend':              trend,
            'historical_bookings': hist,
            'forecast':           preds
        })

    summary.sort(key=lambda x: x['avg_daily_bookings'], reverse=True)
    _cache['summary'] = summary
    return summary


def get_monthly_demand_forecast(equipment_type, months_ahead=6):
    """Monthly aggregated demand forecast."""
    preds = predict_demand_for_equipment(equipment_type, days_ahead=months_ahead * 30)
    df_p  = pd.DataFrame(preds)
    df_p['date']  = pd.to_datetime(df_p['date'])
    df_p['month'] = df_p['date'].dt.strftime('%Y-%m')
    monthly = df_p.groupby('month')['predicted_bookings'].sum().reset_index()
    monthly.columns = ['month', 'total_bookings']
    monthly['total_bookings'] = monthly['total_bookings'].round(1)
    return monthly.to_dict(orient='records')


def warmup():
    """Call this once at app startup to pre-train the model."""
    _load_and_train()
    get_demand_summary()  # pre-build summary cache
