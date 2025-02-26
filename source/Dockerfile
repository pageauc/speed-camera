FROM ubuntu

RUN apt-get update

# avoid any prompts
ENV DEBIAN_FRONTEND noninteractive
# install tzdata package
RUN apt-get install -y tzdata
# set your timezone
RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
RUN dpkg-reconfigure --frontend noninteractive tzdata

# speed camera dependencies
RUN apt-get install -yq python curl wget sudo python-numpy python3-opencv dos2unix python-pil sqlite3  python-matplotlib python3-matplotlib libgl1-mesa-dri pandoc

# set version and install speed camera
ARG SPEED_CAMERA_VER=11.22
RUN curl -L https://raw.github.com/pageauc/rpi-speed-camera/master/speed-install.sh | bash

COPY speed-camera-docker-run.sh /root/speed-camera/speed-camera-docker-run.sh
