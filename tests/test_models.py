from models import BusinessListData, BusinessInsightData, ConfigJson
import pytest


def test_na_rating_becomes_none():
    data = BusinessListData(name="Test", rating="N/A")
    assert data.rating is None


def test_na_email_becomes_none():
    data = BusinessInsightData(name="Test", email="N/A")
    assert data.email is None


def test_name_required():
    with pytest.raises(Exception):
        BusinessListData()


def test_valid_rating():
    data = BusinessListData(name="Test", rating=4.5)
    assert data.rating == 4.5


def test_config_page_limit_over():
    with pytest.raises(Exception):
        ConfigJson(page_per_request=200)


def test_config_valid():
    config = ConfigJson(
        page_per_request=10,
        rate_min=1.0,
        rate_max=2.0,
        max_attempt=3,
        attempt_duration=10.0,
        redo_on_fail_page=False,
        redo_on_fail_page_attempt=2,
        category="accounting",
        location="NYC NY",
        header={"cookies_string": ""},
        amount_write_business_insight=100,
    )
    assert config.page_per_request == 10


def test_na_becomes_none_multiple_fields():
    data = BusinessListData(name="Test", rating="N/A", telephone="N/A", country="N/A")
    assert data.rating is None
    assert data.telephone is None
    assert data.country is None


def test_valid_business_full():
    data = BusinessListData(
        name="Test Business",
        rating=4.5,
        review_count=100,
        telephone="212-555-0100",
        country="US",
    )
    assert data.name == "Test Business"
    assert data.review_count == 100
