FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

RUN mkdir /kororientak
WORKDIR /kororientak

COPY docker/start.sh /kororientak/
COPY requirements /kororientak/requirements
RUN pip install -r requirements/prod.txt

COPY kororientak /kororientak/kororientak

EXPOSE 8000

CMD ["./start.sh"]
