from flask import Blueprint, render_template, redirect, url_for, flash, request
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

@bp.route('/auth/reset_password', methods=['GET', 'POST'])
def reset_password():
    # Implementation for password reset
    pass

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

