FROM python:3
COPY /app /etc/usr/src/app
WORKDIR /etc/usr/src/app
RUN pip3 install paho-mqtt
RUN pip3 install requests
RUN pip install Flask Flask-Cors requests
ENTRYPOINT ["python"]
CMD ["router_msg.py"]
