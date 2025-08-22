FROM python:3.13-slim

COPY requirements.txt /tmp
RUN pip3 install --upgrade -r /tmp/requirements.txt
COPY lib /usr/local/epp-client/lib
COPY epp.py /usr/local/epp-client

ARG SOURCE_BRANCH
RUN echo ${SOURCE_BRANCH} > /usr/local/epp-client/VERSION

WORKDIR /usr/local/epp-client
ENTRYPOINT ["python3", "/usr/local/epp-client/epp.py"]
