from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash
from app import db
from .forms import RegistrationForm
from .models import User


bp = Blueprint ('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@bp.route('/api/login', methods=['POST'])
def api_login():
    from flask import jsonify

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    print(f"🔐 Login attempt: {email}")
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user)
        return jsonify({"status": "success", "message": "Login successful", "user_id": user.id}), 200
    else:
        return jsonify({"status": "fail", "message": "Invalid credentials"}), 401



@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    print("Incoming data:", data)

    try:
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400

        user = User(email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        print("Exception during registration:", str(e))
        return jsonify({'error': str(e)}), 500


@bp.route('/auth/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.reset_password'))

        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)  # Hash and set password
            db.session.commit()
            flash('Password reset successfully. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email not found.', 'danger')
            return redirect(url_for('auth.reset_password'))

    return render_template('reset_password.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

