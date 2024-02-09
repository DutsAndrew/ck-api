import pytest
from controllers.calendar_controller import fetch_calendar_app_data

def test_fetch_calendar_app_data(test_client_with_db):

    response = test_client_with_db.get(
        '/calendar/',
        headers={'content-type': 'application/json'}
    )

    assert response.status_code == 200
    assert response.json() == {
        'detail': 'Calendar Data Loaded',
        'data': {
            '_id': str,
            "app_data_type": "calendar",
            "calendar_dates": {
                "2023": {
                    "January": {
                        "days": 31,
                        "month_starts_on": "Thursday",
                    }
                }
            }
        }
    }