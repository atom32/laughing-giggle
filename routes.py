from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Farm, Crop, Plot
from utils import login_required, admin_required, get_current_user

def init_routes(app):
    
    @app.route('/')
    def home():
        user = get_current_user()
        if user:
            return render_template('dashboard.html', user=user)
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.is_active and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['username'] = user.username
                user.last_login = datetime.utcnow()
                db.session.commit()
                flash(f'Welcome back, Farmer {user.username}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid credentials or account disabled!', 'error')
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out!', 'info')
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists!', 'error')
            elif User.query.filter_by(email=email).first():
                flash('Email already registered!', 'error')
            else:
                user = User(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password)
                )
                db.session.add(user)
                db.session.commit()
                
                # Create starting farm
                farm = Farm(
                    name=f"{username}'s Farm",
                    user_id=user.id,
                    size=6
                )
                db.session.add(farm)
                db.session.commit()
                
                # Create empty plots for the farm
                for i in range(farm.size):
                    plot = Plot(farm_id=farm.id)
                    db.session.add(plot)
                db.session.commit()
                
                flash('Registration successful! Welcome to farming life!', 'success')
                return redirect(url_for('login'))
        
        return render_template('register.html')

    @app.route('/admin')
    @admin_required
    def admin_panel():
        users = User.query.all()
        return render_template('admin.html', users=users)

    @app.route('/admin/toggle_user/<int:user_id>')
    @admin_required
    def toggle_user_status(user_id):
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        status = "activated" if user.is_active else "deactivated"
        flash(f'Farmer {user.username} has been {status}!', 'success')
        return redirect(url_for('admin_panel'))

    @app.route('/admin/make_admin/<int:user_id>')
    @admin_required
    def make_admin(user_id):
        user = User.query.get_or_404(user_id)
        user.is_admin = True
        db.session.commit()
        flash(f'{user.username} is now an admin!', 'success')
        return redirect(url_for('admin_panel'))

    @app.route('/profile')
    @login_required
    def profile():
        user = get_current_user()
        return render_template('profile.html', user=user)

    @app.route('/farm')
    @login_required
    def farm_view():
        user = get_current_user()
        farm = user.farms[0] if user.farms else None
        crops = Crop.query.all()
        return render_template('farm.html', user=user, farm=farm, crops=crops)

    @app.route('/plant/<int:plot_id>/<int:crop_id>')
    @login_required
    def plant_crop(plot_id, crop_id):
        user = get_current_user()
        plot = Plot.query.get_or_404(plot_id)
        crop = Crop.query.get_or_404(crop_id)
        
        # Check if plot belongs to user's farm
        if plot.farm.user_id != user.id:
            flash('This is not your farm!', 'error')
            return redirect(url_for('farm_view'))
        
        # Check if user has enough coins
        if user.coins < crop.buy_price:
            flash('Not enough coins to buy seeds!', 'error')
            return redirect(url_for('farm_view'))
        
        # Check if plot is empty
        if plot.crop_id is not None:
            flash('Plot is already planted!', 'error')
            return redirect(url_for('farm_view'))
        
        # Plant the crop
        user.coins -= crop.buy_price
        plot.crop_id = crop.id
        plot.planted_at = datetime.utcnow()
        plot.is_ready = False
        
        db.session.commit()
        flash(f'Planted {crop.name} successfully!', 'success')
        return redirect(url_for('farm_view'))

    @app.route('/harvest/<int:plot_id>')
    @login_required
    def harvest_crop(plot_id):
        user = get_current_user()
        plot = Plot.query.get_or_404(plot_id)
        
        # Check if plot belongs to user's farm
        if plot.farm.user_id != user.id:
            flash('This is not your farm!', 'error')
            return redirect(url_for('farm_view'))
        
        if not plot.crop_id or not plot.is_ready:
            flash('Nothing ready to harvest!', 'error')
            return redirect(url_for('farm_view'))
        
        # Harvest the crop
        crop = plot.crop
        user.coins += crop.sell_price
        user.experience += crop.experience_gain
        
        # Level up check
        if user.experience >= user.level * 100:
            user.level += 1
            flash(f'Congratulations! You reached level {user.level}!', 'success')
        
        # Clear the plot
        plot.crop_id = None
        plot.planted_at = None
        plot.is_ready = False
        
        db.session.commit()
        flash(f'Harvested {crop.name} for {crop.sell_price} coins!', 'success')
        return redirect(url_for('farm_view'))