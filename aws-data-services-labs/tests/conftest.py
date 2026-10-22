import os
import pytest
from moto import mock_aws

os.environ.update(AWS_ACCESS_KEY_ID="testing", AWS_SECRET_ACCESS_KEY="testing", AWS_SESSION_TOKEN="testing", AWS_REGION="ap-south-1", AWS_DEFAULT_REGION="ap-south-1")


@pytest.fixture
def aws():
    with mock_aws():
        yield
