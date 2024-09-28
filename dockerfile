FROM python:slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt gunicorn pymysql cryptography


COPY App App
COPY migrations migrations
COPY blog.py config.py boot.sh ./
RUN chmod 755 boot.sh

ENV FLASK_APP blog.py
RUN flask translate compile

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]
