import datetime
import logging
import os
from typing import List

from covid_client import CovidRestClient
from flask import Flask, request
from flask_pydantic import validate
from flask_restful import Api, Resource, abort
from flask_sqlalchemy import SQLAlchemy
from iso3166 import Country, countries
from models import TrackSubscribeBodyModel, is_valid_iso_3166_1

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s]:%(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()
app = Flask(__name__)
api = Api(app)
db_path = os.path.join(os.path.dirname(__file__), "cov.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
db = SQLAlchemy(app)

covid_client = CovidRestClient()


class Tracked(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alpha2 = db.Column(db.String(2), unique=True)
    # todo - add some cached info?


def _not_tracked(to_check: List[Country]):
    already_tracked = (
        db.session.query(Tracked.alpha2)
        .filter(Tracked.alpha2.in_([country.alpha2 for country in to_check]))
        .all()
    )
    # convert to flat List[str] like ["POL", "DEU", ...]
    already_tracked = list(sum(already_tracked, ()))
    return set(country for country in to_check if country.alpha2 not in already_tracked)


class TrackSubscribe(Resource):
    @validate(body=TrackSubscribeBodyModel)
    def post(self):
        """Add list of countries to tracked."""
        to_create = _not_tracked(request.body_params.country_codes)
        logger.info("Updating tracked countries with %s", to_create)
        for country in to_create:
            tracked = Tracked(alpha2=country.alpha2)
            db.session.add(tracked)
            db.session.commit()
        return list(country.alpha2 for country in to_create), 201

    @validate(body=TrackSubscribeBodyModel)
    def delete(self):
        """Delete list of countries from tracked"""
        to_delete = request.body_params.country_codes
        not_tracked = _not_tracked(to_delete)
        if not_tracked:
            abort(
                404,
                message=f"Countries {not_tracked} are not tracked! No operations were performed.",
            )
        for country in to_delete:
            tracked = db.session.query(Tracked).filter_by(alpha2=country.alpha2).first()
            db.session.delete(tracked)
            db.session.commit()
        return list(country.alpha2 for country in to_delete), 201


def fetch_country_cov_data(country: Country, date):
    try:
        date = datetime.date.fromisoformat(date)
    except ValueError as e:
        abort(
            400, message=repr(e),
        )
    cov_response = covid_client.get(
        f"country/{country.alpha2}",
        params={
            "from": datetime.datetime.combine(date, datetime.time(0, 0, 0)).isoformat()
            + "Z",
            "to": datetime.datetime.combine(date, datetime.time(23, 59, 59)).isoformat()
            + "Z",
        },
    )
    if not cov_response.ok:
        # todo Not sure of proper status code here
        abort(
            400, message=cov_response.text,
        )
    cov_json = cov_response.json()[0]
    return dict(
        (key, cov_json[key]) for key in ("Country", "Active", "Deaths", "Recovered")
    )


class TrackedFetch(Resource):
    def get(self, date):
        """Get covid details about tracked countries."""
        tracked = Tracked.query.all()
        return {
            "countries": list(
                fetch_country_cov_data(country, date) for country in tracked
            ),
            "date": date,
        }


class Countries(Resource):
    def get(self, country: Country, date):
        if not is_valid_iso_3166_1(country):
            abort(
                400, message=f"{country} is not valid ISO 3166 Country Code!",
            )
        return {
            **fetch_country_cov_data(countries.get(country), date),
            "date": date,
        }


api.add_resource(Countries, "/countries/<string:country>/<string:date>")
api.add_resource(TrackedFetch, "/tracked/<string:date>")
api.add_resource(TrackSubscribe, "/tracked")
