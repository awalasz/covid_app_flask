FROM tiangolo/meinheld-gunicorn-flask:python3.8
COPY ./app/requirements.txt /app/requirements.txt
RUN pip3.8 install -r /app/requirements.txt
COPY ./app /app
RUN python3.8 -c "from main import db; db.create_all()"


