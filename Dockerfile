FROM alpine:3.6

ADD flaskapp.y /root/flaskapp.py
ADD requirements.txt /root/requirements.txt
RUN pip install -r /root/requirements.txt
EXPOSE [443]
CMD ['python /root/flaskapp.py']
