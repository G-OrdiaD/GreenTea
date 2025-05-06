import random
from datetime import datetime
from app.models import SensorData, SensorParameter, Greenhouse
from app import db
from flask import Flask
from app import create_app

def simulate_sensor_data(app):
    with app.app_context():
        greenhouses = Greenhouse.query.all()
        parameters = SensorParameter.query.all()

        if not greenhouses or not parameters:
            print("Warning: No greenhouses or sensor parameters found in the database.")
            return

        for gh in greenhouses:
            for param in parameters:
                if param.min_value is not None and param.max_value is not None:
                    # Simulate a reading that might trigger an issue (20% chance)
                    if random.random() < 0.2:
                        # 50% chance of being low, 50% chance of being high
                        if random.random() < 0.5:
                            simulated_value = param.min_value - random.uniform(1, 10)
                        else:
                            simulated_value = param.max_value + random.uniform(1, 10)
                    else:
                        # Simulate a reading within the normal range
                        simulated_value = random.uniform(param.min_value, param.max_value)

                    new_sensor_data = SensorData(
                        greenhouse_id=gh.id,
                        parameter_id=param.id,
                        value=simulated_value,
                        timestamp=datetime.now()
                    )
                    db.session.add(new_sensor_data)
            db.session.commit()
        print("Simulated sensor data added for all greenhouses and parameters.")

if __name__ == '__main__':
    app = create_app()
    simulate_sensor_data(app)