from flask import render_template, request, redirect, url_for, session, flash
from flask_babel import gettext as _, ngettext
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Farm, Crop, Plot
from utils import login_required, admin_required, get_current_user
from config.i18n import safe_translate, translate_error, translate_success

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
                # Load user's preferred language into session
                session['language'] = user.preferred_language or 'en'
                user.last_login = datetime.utcnow()
                db.session.commit()
                flash(_('Welcome back, Farmer %(username)s!', username=user.username), 'success')
                return redirect(url_for('home'))
            else:
                flash(_('Invalid credentials or account disabled!'), 'error')
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash(_('You have been logged out!'), 'info')
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            if User.query.filter_by(username=username).first():
                flash(_('Username already exists!'), 'error')
            elif User.query.filter_by(email=email).first():
                flash(_('Email already registered!'), 'error')
            else:
                # Get configuration for starting resources
                config = app.config.get('APP_CONFIG')
                if config:
                    starting_resources = config.get_starting_resources()
                    starting_coins = starting_resources['coins']
                    starting_wheat = starting_resources['wheat']
                    starting_corn = starting_resources['corn']
                    starting_carrots = starting_resources['carrots']
                    farm_size = starting_resources['farm_size']
                else:
                    # Fallback to hardcoded values
                    starting_coins = 1000
                    starting_wheat = 50
                    starting_corn = 30
                    starting_carrots = 20
                    farm_size = 6
                
                # Detect browser language for new user
                from config.i18n import detect_browser_language, DEFAULT_LANGUAGE
                detected_language = detect_browser_language() or DEFAULT_LANGUAGE
                
                user = User(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    coins=starting_coins,
                    wheat=starting_wheat,
                    corn=starting_corn,
                    carrots=starting_carrots,
                    preferred_language=detected_language
                )
                db.session.add(user)
                db.session.commit()
                
                # Create starting farm
                farm = Farm(
                    name=_("%(username)s's Farm", username=username),
                    user_id=user.id,
                    size=farm_size
                )
                db.session.add(farm)
                db.session.commit()
                
                # Create empty plots for the farm
                for i in range(farm.size):
                    plot = Plot(farm_id=farm.id)
                    db.session.add(plot)
                db.session.commit()
                
                flash(_('Registration successful! Welcome to farming life!'), 'success')
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
        if user.is_active:
            flash(_('Farmer %(username)s has been activated!', username=user.username), 'success')
        else:
            flash(_('Farmer %(username)s has been deactivated!', username=user.username), 'success')
        return redirect(url_for('admin_panel'))

    @app.route('/admin/make_admin/<int:user_id>')
    @admin_required
    def make_admin(user_id):
        user = User.query.get_or_404(user_id)
        user.is_admin = True
        db.session.commit()
        flash(_('%(username)s is now an admin!', username=user.username), 'success')
        return redirect(url_for('admin_panel'))

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        user = get_current_user()
        
        if request.method == 'POST':
            # Handle language preference update
            if 'preferred_language' in request.form:
                new_language = request.form['preferred_language']
                from config.i18n import is_language_supported
                
                if is_language_supported(new_language):
                    user.preferred_language = new_language
                    session['language'] = new_language
                    db.session.commit()
                    flash(_('Language preference updated successfully!'), 'success')
                else:
                    flash(_('Invalid language selection!'), 'error')
                
                return redirect(url_for('profile'))
        
        # Get available languages for the dropdown
        from config.i18n import get_available_languages
        available_languages = get_available_languages()
        
        return render_template('profile.html', user=user, available_languages=available_languages)

    @app.route('/set_language/<language>')
    def set_language(language):
        """Set user's language preference and redirect back to previous page."""
        from config.i18n import is_language_supported
        
        if not is_language_supported(language):
            flash(_('Invalid language selection!'), 'error')
            return redirect(request.referrer or url_for('home'))
        
        # Set language in session for immediate effect
        session['language'] = language
        
        # If user is logged in, save preference to database
        user = get_current_user()
        if user:
            user.preferred_language = language
            db.session.commit()
            flash(_('Language preference updated successfully!'), 'success')
        
        # Redirect back to the page the user came from
        return redirect(request.referrer or url_for('home'))

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
            flash(_('This is not your farm!'), 'error')
            return redirect(url_for('farm_view'))
        
        # Check if user has enough coins
        if user.coins < crop.buy_price:
            flash(_('Not enough coins to buy seeds!'), 'error')
            return redirect(url_for('farm_view'))
        
        # Check if plot is empty
        if plot.crop_id is not None:
            flash(_('Plot is already planted!'), 'error')
            return redirect(url_for('farm_view'))
        
        # Plant the crop
        user.coins -= crop.buy_price
        plot.crop_id = crop.id
        plot.planted_at = datetime.utcnow()
        plot.is_ready = False
        
        db.session.commit()
        flash(_('Planted %(crop_name)s successfully!', crop_name=crop.name), 'success')
        return redirect(url_for('farm_view'))

    @app.route('/harvest/<int:plot_id>')
    @login_required
    def harvest_crop(plot_id):
        user = get_current_user()
        plot = Plot.query.get_or_404(plot_id)
        
        # Check if plot belongs to user's farm
        if plot.farm.user_id != user.id:
            flash(_('This is not your farm!'), 'error')
            return redirect(url_for('farm_view'))
        
        if not plot.crop_id or not plot.is_ready:
            flash(_('Nothing ready to harvest!'), 'error')
            return redirect(url_for('farm_view'))
        
        # Harvest the crop
        crop = plot.crop
        user.coins += crop.sell_price
        user.experience += crop.experience_gain
        
        # Level up check - use configuration for experience per level
        config = app.config.get('APP_CONFIG')
        if config:
            game_settings = config.get_game_settings()
            experience_per_level = game_settings['experience_per_level']
            max_level = game_settings['max_level']
        else:
            # Fallback to hardcoded values
            experience_per_level = 100
            max_level = 100
        
        if user.experience >= user.level * experience_per_level and user.level < max_level:
            user.level += 1
            flash(_('Congratulations! You reached level %(level)d!', level=user.level), 'success')
        
        # Clear the plot
        plot.crop_id = None
        plot.planted_at = None
        plot.is_ready = False
        
        db.session.commit()
        flash(_('Harvested %(crop_name)s for %(coins)d coins!', crop_name=crop.name, coins=crop.sell_price), 'success')
        return redirect(url_for('farm_view'))