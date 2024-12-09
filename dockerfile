FROM python:3.12-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt 
RUN pip install gunicorn pymysql cryptography


COPY App/ App/
COPY migrations/ migrations/
COPY blog.py config.py boot.sh ./
RUN chmod 755 boot.sh

ENV FLASK_APP=blog.py
# RUN flask translate compile

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]