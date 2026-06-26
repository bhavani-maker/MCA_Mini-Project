from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

def generate_receipt_pdf(booking_data, lang='en', translations_dict=None):
    """
    Generate a PDF receipt for a booking
    
    Args:
        booking_data: Dictionary containing booking information
        lang: Language code (en, te, kn, hi, ta)
        translations_dict: Translation dictionary
    
    Returns:
        Path to generated PDF file
    """
    from receipt_translations import t
    
    # Create receipts directory if it doesn't exist
    receipts_dir = os.path.join('static', 'receipts')
    os.makedirs(receipts_dir, exist_ok=True)
    
    # Generate filename
    filename = f"receipt_{booking_data['booking_id']}_{lang}.pdf"
    filepath = os.path.join(receipts_dir, filename)
    
    # Create PDF
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # Try to register Unicode font for Indian languages
    try:
        # For production, you'd need to include appropriate fonts
        # For now, we'll use default fonts with best effort
        pass
    except:
        pass
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 1*inch, "KrushiRent AI")
    
    c.setFont("Helvetica-Bold", 18)
    title = t('receipt', lang)
    c.drawCentredString(width/2, height - 1.5*inch, title)
    
    # Line separator
    c.line(1*inch, height - 1.7*inch, width - 1*inch, height - 1.7*inch)
    
    # Booking details
    y_position = height - 2.2*inch
    c.setFont("Helvetica", 12)
    
    details = [
        (t('booking_id', lang), booking_data.get('booking_id', 'N/A')),
        (t('transaction_id', lang), booking_data.get('transaction_id', 'N/A')),
        (t('customer_name', lang), booking_data.get('farmer_name', 'N/A')),
        (t('phone', lang), booking_data.get('farmer_phone', 'N/A')),
        (t('address', lang), booking_data.get('farmer_location', 'N/A')),
        (t('equipment_name', lang), booking_data.get('equipment_name', 'N/A')),
        (t('duration', lang), f"{booking_data.get('duration_hours', 0)} {t('hours', lang)}"),
        (t('amount', lang), f"₹{booking_data.get('total_amount', 0)}"),
        (t('date_time', lang), booking_data.get('payment_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))),
        (t('payment_status', lang), t('success', lang))
    ]
    
    for label, value in details:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1.5*inch, y_position, f"{label}:")
        c.setFont("Helvetica", 12)
        c.drawString(3.5*inch, y_position, str(value))
        y_position -= 0.3*inch
    
    # Footer line
    c.line(1*inch, y_position - 0.3*inch, width - 1*inch, y_position - 0.3*inch)
    
    # Thank you message
    c.setFont("Helvetica-Oblique", 14)
    thank_you = t('thankyou', lang)
    c.drawCentredString(width/2, y_position - 0.7*inch, thank_you)
    
    # Footer
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 0.5*inch, "This is a computer-generated receipt")
    
    c.save()
    return filepath
