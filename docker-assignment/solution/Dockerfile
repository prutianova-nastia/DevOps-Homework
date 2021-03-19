FROM ubuntu:bionic

ADD requirements.txt requirements.txt
RUN echo installing \
    && apt-get update -qq \
    && apt-get install -y \
        python3 \
        python3-pip \
    && pip3 install -r requirements.txt

COPY . .

CMD python3 app.py

