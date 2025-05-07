from datetime import datetime, timedelta
from app.models import SensorData, SensorParameter, Issue, db


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