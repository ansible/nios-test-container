FROM alpine:3.15

ADD flaskapp.py /root/flaskapp.py
ADD requirements.txt /root/requirements.txt
RUN apk add --no-cache build-base python3 py3-wheel py3-pip py3-cryptography
RUN pip3 install -r /root/requirements.txt
EXPOSE 443
CMD /usr/bin/python3 /root/flaskapp.py
