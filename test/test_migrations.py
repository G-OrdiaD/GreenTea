import unittest
from unittest.mock import MagicMock, patch
from app.utils.monitoring import check_sensor_readings

class MonitoringTest(unittest.TestCase):

    @patch('app.utils.monitoring.db')
    @patch('app.utils.monitoring.Issue')
    @patch('app.utils.monitoring.SensorData')
    @patch('app.utils.monitoring.SensorParameter')
    def test_issue_created_if_reading_out_of_range(self, MockSensorParameter, MockSensorData, MockIssue, MockDb):
        # Create a mock sensor parameter
        param = MagicMock()
        param.id = 1
        param.min_value = 10
        param.max_value = 20
        MockSensorParameter.query.all.return_value = [param]

        reading = MagicMock()
        reading.parameter_id = 1
        reading.value = 25
        reading.greenhouse_id = 100

        MockSensorData.query.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = [reading]

        MockIssue.query.filter_by.return_value.first.return_value = None

        check_sensor_readings()

        self.assertTrue(MockDb.session.add.called)
        self.assertTrue(MockDb.session.commit.called)