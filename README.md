# Flask Covid-19 API

## About

The application is fetching data from available for free [COVID 19 API](https://covid19api.com/).

## Deployment with docker

Deployment with docker is the easiest way to start an app. Just simply build an image:

    docker build -t covid_app ./
    
When image is built, simply run application in a container with:

    docker run -d -p 80:80 covid_app

> to install docker, please follow the instructions from [official docker site](https://docs.docker.com/get-docker/).

## Usage

### Get information about specific country:

To get an information about specific country use following url: `<host>/countries/<COUNTRY_CODE>/<DATE>`

- `COUNTRY_CODE` should be valid ISO 3166 Country Code, for example Poland / PL / POL
- `DATE` should be in `yyyy-mm-dd` format 

Examples:

    curl --header "Content-Type: application/json" \
      --request GET \
      http://localhost/countries/de/2020-09-09

  
    curl --header "Content-Type: application/json" \
      --request GET \
      http://localhost/countries/poland/2020-09-09
      
### Tracking countries:

For frequently checked countries user may store tracked countries in database. To add countries to list of tracked
countries send POST request to url `<host>/tracked` like:

    curl --header "Content-Type: application/json" \
      --request POST \
      --data '{"country_codes": ["DE", "RUS", "NL"]}' \
      http://localhost/tracked

To remove countries from tracking, use DELETE method to the same endpoint with similar request body:

    curl --header "Content-Type: application/json" \
      --request DELETE \
      --data '{"country_codes": ["RUS"]}' \
      http://localhost/tracked

Getting covid data for all tracked countries:

    curl --header "Content-Type: application/json" \
      --request GET \
      http://localhost/tracked/2020-09-09
