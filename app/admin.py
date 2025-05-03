from flask import request, redirect,render_template, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from app.forms import ParameterForm
from werkzeug.security import generate_password_hash
from .models import db, User, GreenhouseAssignment, SensorParameter
from .utils.sms_utils import send_sms_alert
from flask import Blueprint
from app import db


bp = Blueprint('admin', __name__)

@bp.route('/admin/assign', methods=['POST'])
@login_required
def assign_greenhouse():
    current_app.logger.info(f"Assignment attempt by user {current_user.id}")

    if current_user.role != 'admin':
        print(f"🚨 Unauthorized assignment attempt by user {current_user.id} (Role: {current_user.role})") # Log authorization check
        return jsonify({"error": "Unauthorized"}), 403

    try:
        employee_id = request.json.get('employee_id')
        greenhouse_id = request.json.get('greenhouse_id')
        print(f"📥 Assignment request - Employee: {employee_id}, Greenhouse: {greenhouse_id}") # Log incoming request data

        assignment = GreenhouseAssignment(
            employee_id=employee_id,
            greenhouse_id=greenhouse_id
        )

        db.session.add(assignment)
        db.session.commit()

        print(
            f"✅ Successfully assigned Greenhouse {greenhouse_id} to Employee {employee_id} (Assignment ID: {assignment.id})") # Log successful assignment

        return jsonify({
            "status": "success",
            "assignment": {
                "id": assignment.id,
                "greenhouse": assignment.greenhouse.name,
                "employee": assignment.employee.username
            }
        })

    except Exception as e:
        # Log any errors
        print(f"❌ Assignment failed: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500


@bp.route('/admin/users')
@login_required
def list_users():
    if current_user.role != 'admin':
        if request.accept_mimetypes.accept_json:
            return jsonify({"error": "Unauthorized"}), 403
        else:
            flash("You are not authorized to access this page.", "danger")
            return redirect(url_for('main.dashboard'))

    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/parameters', methods=['GET', 'POST'])
@login_required
def manage_parameters():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))

    form = ParameterForm()
    if form.validate_on_submit():
        param = SensorParameter(
            name=form.name.data,
            min_value=form.min_value.data,
            max_value=form.max_value.data,
            unit=form.unit.data
        )
        db.session.add(param)
        db.session.commit()
        flash('Parameter added successfully', 'success')
        return redirect(url_for('admin.manage_parameters'))

    parameters = SensorParameter.query.all()
    return render_template('admin/parameters.html', form=form, parameters=parameters)