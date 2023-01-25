FROM quay.io/bedrock/alpine:3.17.1

RUN apk add --no-cache python3

RUN python -m venv /root/venv
RUN /root/venv/bin/pip install --disable-pip-version-check --no-cache wheel==0.38.4  # avoid pip warning when installing Flask-BasicAuth

ADD requirements.txt /root/requirements.txt
ADD constraints.txt /root/constraints.txt

RUN /root/venv/bin/pip install --disable-pip-version-check --no-cache -r /root/requirements.txt -c /root/constraints.txt

ADD flaskapp.py /root/flaskapp.py
CMD /root/venv/bin/python /root/flaskapp.py

EXPOSE 443
