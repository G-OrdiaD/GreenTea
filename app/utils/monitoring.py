from datetime import datetime, timedelta
from app.models import SensorData, SensorParameter, Issue, db, OptimalRange


def check_sensor_readings():
    parameters = SensorParameter.query.all()

    for param in parameters:
        latest_readings = SensorData.query.filter_by(
            parameter_id=param.id
        ).order_by(
            SensorData.timestamp.desc()
        ).limit(50).all()

        for reading in latest_readings:
            if reading.value < param.min_value or reading.value > param.max_value:
                # Check if issue already exists
                existing_issue = Issue.query.filter_by(
                    greenhouse_id=reading.greenhouse_id,
                    parameter_id=param.id,
                    status='Open'
                ).first()

                if not existing_issue:
                    # Determine priority
                    if (reading.value < param.min_value * 0.8 or
                            reading.value > param.max_value * 1.2):
                        priority = 'Critical'
                    else:
                        priority = 'High'

                    # Create new issue
                    new_issue = Issue(
                        greenhouse_id=reading.greenhouse_id,
                        parameter_id=param.id,
                        priority=priority,
                        status='Open',
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(new_issue)

    db.session.commit()


def insert_default_optimal_ranges():

    if not OptimalRange.query.filter_by(parameter="temperature").first():
        temperature_range = OptimalRange(parameter="temperature", min_value=13.5, max_value=28.0)
        db.session.add(temperature_range)

    if not OptimalRange.query.filter_by(parameter="humidity").first():
        humidity_range = OptimalRange(parameter="humidity", min_value=30.0, max_value=90.0)
        db.session.add(humidity_range)

    if not OptimalRange.query.filter_by(parameter="pH").first():
        ph_range = OptimalRange(parameter="pH", min_value=5.0, max_value=7.5)
        db.session.add(ph_range)

    if not OptimalRange.query.filter_by(parameter="air_quality").first():
        airquality_range = OptimalRange(parameter="air_quality", min_value=700, max_value=1500)
        db.session.add(airquality_range)

    if not OptimalRange.query.filter_by(parameter="light_intensity").first():
        lightintensity_range = OptimalRange(parameter="light_intensity", min_value=500, max_value=2000)
        db.session.add(lightintensity_range)

    db.session.commit()