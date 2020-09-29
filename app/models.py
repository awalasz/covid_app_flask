from typing import List, Union

from iso3166 import Country, countries
from pydantic import BaseModel, validator


def is_valid_iso_3166_1(value):
    """Checks if value is valid country code."""
    return countries.get(value, None) is not None


class TrackSubscribeBodyModel(BaseModel):
    """country_codes are list of ISO 3166-1 country codes. ISO 3166-1 defines two-letter, three-letter, and three-digit
    country codes, But full country name is also accepted in this application (TODO - ask for requirements here)
    For example for Poland all of this are valid: Poland, PL, POL, 616.


    For most of countries apolitical name will be the same as name."""

    country_codes: List[Union[str, int, Country]]

    @validator("country_codes")
    def is_valid_iso_3166_1(cls, codes):
        invalid_country_codes = [
            code for code in codes if not is_valid_iso_3166_1(code)
        ]
        if invalid_country_codes:
            raise ValueError(
                f"{invalid_country_codes} are not valid a ISO 3166-1 country codes"
            )
        return list({countries.get(code) for code in codes})  # rm duplicates
