import pytest

from app.models import TrackSubscribeBodyModel, is_valid_iso_3166_1


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Poland", True),  # todo - not sure about full name.
        ("PL", True),
        ("POL", True),
        ("pl", True),
        ("pol", True),
        ("616", True),
        (616, True),
        ("foo", False),
    ],
)
def test_is_valid_iso_3166_1(value, expected):
    assert is_valid_iso_3166_1


def test_tracking_body_model():
    body = TrackSubscribeBodyModel.parse_obj({"country_codes": ["POL", "de", "France"]})
    assert len(body.country_codes) == 3


def test_duplicated_country_codes():
    body = TrackSubscribeBodyModel.parse_obj({"country_codes": ["POL", "pl", "Poland"]})
    assert len(body.country_codes) == 1
    assert body.country_codes[0].name == "Poland"


def test_invalid_country_code():
    with pytest.raises(ValueError):
        _ = TrackSubscribeBodyModel.parse_obj({"country_codes": ["foo", "bar"]})


def test_invalid_body():
    with pytest.raises(ValueError):
        _ = TrackSubscribeBodyModel.parse_obj({"baz": ["PL", "DE"]})
