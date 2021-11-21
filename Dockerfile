FROM alpine:3.14

ADD flaskapp.py /root/flaskapp.py
ADD requirements.txt /root/requirements.txt
RUN apk add --no-cache build-base openssl-dev libffi-dev python3 python3-dev py3-pip cargo
RUN pip3 install -r /root/requirements.txt
EXPOSE 443
CMD /usr/bin/python3 /root/flaskapp.py
