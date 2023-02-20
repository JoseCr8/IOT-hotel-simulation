FROM debian:buster
RUN apt update
RUN apt install mosquitto mosquitto-clients -y
RUN touch /etc/mosquitto/passwd
RUN mosquitto_passwd -b /etc/mosquitto/passwd dso_user dso_password
CMD ["/usr/sbin/mosquitto","-c","/etc/mosquitto/mosquitto.conf"]
