FROM python:3
RUN pip3 install paho-mqtt
COPY /app /etc/usr/src/app
WORKDIR /etc/usr/src/app
ENTRYPOINT ["python"]
CMD ["twin.py"]
