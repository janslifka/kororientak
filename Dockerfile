FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

RUN mkdir /kororientak
WORKDIR /kororientak

COPY manage.py /kororientak/
COPY start.sh /kororientak/
COPY requirements.txt /kororientak/
RUN pip install -r requirements.txt

COPY ./kororientak /kororientak/kororientak
COPY ./competition /kororientak/competition

EXPOSE 8000

CMD ["./start.sh"]
