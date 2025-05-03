from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app.models import db, SensorParameter, SensorData, Greenhouse, Feedback, Issue
from .utils.sms_utils import send_sms_alert
from flask import Blueprint
from app import db
from flask_login import login_required, current_user
from .forms import ParameterForm
from .utils.monitoring import check_sensor_readings


bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('home.html')


@bp.route('/dashboard')
@login_required
def dashboard():

    from .models import SensorData
    sensor_data = SensorData.query.order_by(SensorData.timestamp.desc()).first()

    from .utils.monitoring import check_sensor_readings
    check_sensor_readings()

    critical_issues = Issue.query.filter_by(priority='Critical').count()
    open_issues = Issue.query.filter_by(status='Open').count()
    resolved_issues = Issue.query.filter_by(status='Resolved').count()

    greenhouses = Greenhouse.query.all()
    parameters = SensorParameter.query.all()

    return render_template('dashboard.html',
                           data=sensor_data,
                           greenhouses=greenhouses,
                           parameters=parameters,
                           critical_issues=critical_issues,
                           open_issues=open_issues)


@bp.route('/issues')
def get_issues():
    """Returns all issues (optionally filtered by status) as JSON."""
    status_filter = request.args.get('status')
    include_resolved = request.args.get('include_resolved', 'false').lower() == 'true'

    query = Issue.query.join(Greenhouse).join(SensorParameter)

    if status_filter:
        query = query.filter_by(status=status_filter)
    elif not include_resolved:
        query = query.filter(Issue.status != 'Resolved')

    issues = query.order_by(Issue.timestamp.desc()).all()

    issues_data = []
    for issue in issues:
        issues_data.append({
            'id': issue.id,
            'greenhouse_id': issue.greenhouse_id,
            'greenhouse_name': issue.greenhouse.name,
            'parameter': issue.parameter.name,
            'message': f"Issue with {issue.parameter.name} in {issue.greenhouse.name}",
            'priority': issue.priority,
            'status': issue.status,
            'assigned_to': issue.assigned_to.username if issue.assigned_to else None,
            'timestamp': issue.timestamp.isoformat()
        })

    return jsonify({'issues': issues_data})


@bp.route('/issues/<int:issue_id>')
@login_required
def view_issue(issue_id):
    """View details of a specific issue"""
    issue = Issue.query.get_or_404(issue_id)
    greenhouse = Greenhouse.query.get(issue.greenhouse_id)
    return render_template('view_issue.html',
                         issue=issue,
                         greenhouse=greenhouse)


@bp.route('/issues/<int:issue_id>/update', methods=['POST'])
@login_required
def update_issue_status(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    new_status = request.form.get('status')

    if new_status not in ['Open', 'Fixing', 'Resolved']:
        flash('Invalid status selected.', 'danger')
        return redirect(url_for('main.view_issue', issue_id=issue.id))

    issue.status = new_status
    db.session.commit()

    flash('Issue status updated successfully.', 'success')
    return redirect(url_for('main.view_issue', issue_id=issue.id))


@bp.route('/realtime-monitoring')
@login_required
def realtime_monitoring():
    parameters = SensorParameter.query.all()
    current_readings = SensorData.query.order_by(SensorData.timestamp.desc()).limit(5).all()
    return render_template('realtime_monitoring.html',
                         parameters=parameters,
                         current_readings=current_readings)


@bp.route('/smart-alerts')
@login_required
def smart_alerts():
    active_issues = Issue.query.filter_by(status='Open').order_by(Issue.priority.desc()).all()
    return render_template('smart_alerts.html',
                         active_issues=active_issues)

@bp.route('/data-analytics')
@login_required
def data_analytics():
    return render_template('data_analytics.html')


@bp.route('/api/sensor-data')
@login_required
def get_sensor_data():
    hours = request.args.get('hours', default=24, type=int)
    data = SensorData.query.filter(
        SensorData.timestamp >= datetime.utcnow() - timedelta(hours=hours)
    ).order_by(SensorData.timestamp.asc()).all()

    # Structure data for each sensor type
    temperature_data = {'timestamps': [d.timestamp.isoformat() for d in data], 'values': [d.temperature for d in data]}
    humidity_data = {'timestamps': [d.timestamp.isoformat() for d in data], 'values': [d.humidity for d in data]}
    air_quality_data = {'timestamps': [d.timestamp.isoformat() for d in data], 'values': [d.air_quality for d in data]}
    ph_data = {'timestamps': [d.timestamp.isoformat() for d in data], 'values': [d.ph for d in data]}
    light_intensity_data = {'timestamps': [d.timestamp.isoformat() for d in data], 'values': [d.light_intensity for d in data]}

    return jsonify({
        'temperature': temperature_data,
        'humidity': humidity_data,
        'air_quality': air_quality_data,
        'ph': ph_data,
        'light_intensity': light_intensity_data
    })

@bp.route('/greenhouses')
def list_greenhouses():
    greenhouses = Greenhouse.query.all()
    return render_template('greenhouse_list.html', greenhouses=greenhouses)


@bp.route('/greenhouse/<int:greenhouse_id>')
def greenhouse_detail(greenhouse_id):
    greenhouse = Greenhouse.query.get_or_404(greenhouse_id)
    issues = Issue.query.filter_by(greenhouse_id=greenhouse.id).order_by(Issue.timestamp.desc()).all()
    return render_template('greenhouse_detail.html', greenhouse=greenhouse, issues=issues)


@bp.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    message = request.json.get('message')

    feedback = Feedback(
        user_id=current_user.id,
        message=message
    )
    db.session.add(feedback)
    db.session.commit()

    return jsonify({"status": "success"})