FROM python:3

ADD start.sh /start.sh
ADD requirements.txt /requirements.txt

RUN chmod +x /start.sh && \
    pip install -r /requirements.txt

ENTRYPOINT /start.sh