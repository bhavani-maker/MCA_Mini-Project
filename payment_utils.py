import json
import os
from datetime import datetime
import uuid

def load_payments():
    if os.path.exists('payments.json'):
        with open('payments.json', 'r') as f:
            return json.load(f)
    return {}

def save_payments(payments):
    with open('payments.json', 'w') as f:
        json.dump(payments, f, indent=2)

def create_payment_record(booking_id, order_id, amount, payment_method=None):
    """Create a new payment record"""
    payment_id = str(uuid.uuid4())[:12]
    
    payment_data = {
        'payment_id': payment_id,
        'booking_id': booking_id,
        'order_id': order_id,
        'amount': amount,
        'currency': 'INR',
        'payment_status': 'PENDING',
        'payment_method': payment_method,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    payments = load_payments()
    payments[payment_id] = payment_data
    save_payments(payments)
    
    return payment_data

def update_payment_status(payment_id, status, razorpay_payment_id=None, payment_method=None):
    """Update payment status"""
    payments = load_payments()
    
    if payment_id in payments:
        payments[payment_id]['payment_status'] = status
        payments[payment_id]['updated_at'] = datetime.now().isoformat()
        
        if razorpay_payment_id:
            payments[payment_id]['razorpay_payment_id'] = razorpay_payment_id
        
        if payment_method:
            payments[payment_id]['payment_method'] = payment_method
            
        save_payments(payments)
        return payments[payment_id]
    
    return None

def get_payment_by_order_id(order_id):
    """Get payment record by order ID"""
    payments = load_payments()
    for payment in payments.values():
        if payment['order_id'] == order_id:
            return payment
    return None