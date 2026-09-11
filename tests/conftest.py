from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def activity_data():
    original_activities = deepcopy(activities)
    yield activities
    activities.clear()
    activities.update(original_activities)
