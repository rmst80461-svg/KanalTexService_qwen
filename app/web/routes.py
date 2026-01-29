"""
Web routes for the admin panel
"""
import io
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.database import Database
    from app.bot.bot_handler import TelegramBot

from app.web.services import User, load_user as user_loader_func
from app.config import ADMIN_USERNAME, ADMIN_PASSWORD_HASH


def setup_routes(app: Flask, db: 'Database', telegram_bot: 'TelegramBot' = None):
    """Setup all routes for the Flask app"""
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id: str) -> User:
        return user_loader_func(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page for admin panel"""
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
                user = User(1)  # For simplicity, single admin with ID=1
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Неверный логин или пароль')
        
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        """Logout from admin panel"""
        logout_user()
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def dashboard():
        """Admin dashboard showing requests"""
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page
        
        # Get all requests
        all_requests = db.get_all_requests()
        total_requests = len(all_requests)
        requests = all_requests[offset:offset + per_page]
        
        # Calculate total pages
        total_pages = (total_requests + per_page - 1) // per_page
        
        return render_template('dashboard.html', requests=requests, page=page, total_pages=total_pages)

    @app.route('/update_status/<int:request_id>', methods=['POST'])
    @login_required
    def update_status(request_id: int):
        """Update request status"""
        new_status = request.form['status']
        comment = request.form.get('comment', '')
        
        # Update status in database
        db.update_status(request_id, new_status)
        
        # If there's a comment, update it too
        if comment:
            db.update_comment(request_id, comment)
        
        # Get request info to send notification to user
        request_info = db.get_request_by_id(request_id)
        if request_info and telegram_bot:
            user_id = request_info[1]  # user_id is at index 1
            # Send notification to user via bot in a background task
            import asyncio
            import threading
            
            def send_notification():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(telegram_bot.send_status_update(user_id, request_id, new_status, comment))
                    loop.close()
                except Exception as e:
                    import logging
                    logging.error(f"Error sending notification to user: {e}")
            
            # Run notification in a separate thread to avoid blocking
            notification_thread = threading.Thread(target=send_notification)
            notification_thread.daemon = True
            notification_thread.start()
        
        flash('Статус заявки успешно обновлен!')
        return redirect(url_for('dashboard'))

    @app.route('/export_csv')
    @login_required
    def export_csv():
        """Export all requests to CSV file"""
        # Get all requests
        all_requests = db.get_all_requests()
        
        # Define column headers
        headers = [
            'ID', 'User ID', 'Full Name', 'Address', 'Service Type', 
            'Phone', 'Status', 'Comment', 'Created At'
        ]
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(headers)
        
        # Write data rows
        for row in all_requests:
            writer.writerow(row)
        
        # Get the CSV content
        csv_content = output.getvalue()
        output.close()
        
        # Create BytesIO object for sending
        mem = io.BytesIO()
        mem.write(csv_content.encode('utf-8'))
        mem.seek(0)
        
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'requests_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )