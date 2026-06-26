# Add this code to your krushi_app.py file

@app.route('/admin/reports', methods=['GET'])
def admin_reports():
    """Admin Reports API - Returns equipment usage and revenue data"""
    
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get date filters safely
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        conn = get_db_connection()
        
        # Build query with LEFT JOIN to include equipment with 0 bookings
        query = '''
            SELECT 
                e.id,
                e.name,
                e.type,
                COUNT(b.id) as times_rented,
                COALESCE(SUM(b.total_amount), 0) as revenue
            FROM equipment e
            LEFT JOIN bookings b ON e.id = b.equipment_id
        '''
        
        params = []
        
        # Add date filters if provided
        if start_date and end_date:
            query += ' WHERE b.booking_date BETWEEN ? AND ?'
            params = [start_date, end_date]
        elif start_date:
            query += ' WHERE b.booking_date >= ?'
            params = [start_date]
        elif end_date:
            query += ' WHERE b.booking_date <= ?'
            params = [end_date]
        
        query += ' GROUP BY e.id, e.name, e.type ORDER BY revenue DESC'
        
        # Execute query
        equipment_usage = conn.execute(query, params).fetchall()
        
        # Convert to list of dictionaries
        report_data = []
        for row in equipment_usage:
            report_data.append({
                'id': row['id'],
                'name': row['name'],
                'type': row['type'],
                'times_rented': row['times_rented'],
                'revenue': float(row['revenue'])
            })
        
        conn.close()
        
        # Return success response
        return jsonify({
            'success': True,
            'data': report_data,
            'total_equipment': len(report_data),
            'total_revenue': sum(item['revenue'] for item in report_data)
        }), 200
        
    except Exception as e:
        print(f"Error in admin_reports: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load reports',
            'message': str(e)
        }), 500


def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect('krushi_rent_ai.db')
    conn.row_factory = sqlite3.Row
    return conn
