FROM python:3.12

ENV DEBIAN_FRONTEND=noninteractive

# Create a new user 'james' with password 'semaj'
RUN useradd -m -d /home/james -s /bin/bash james && echo "james:semaj" | chpasswd

# Add user 'james' to the sudoers group
RUN usermod -aG sudo james
RUN echo "james ALL=(ALL) NOPASSWD:ALL" 

# Set working directory
WORKDIR /home/james

# Install necessary packages
RUN apt-get update --fix-missing && apt-get install -y \
    sudo iputils-ping cmake build-essential nodejs npm

# Install Qt dependencies
RUN apt-get install -y '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev libxcb-util1 \ 
    libdbus-1-3 libinput-dev libxcb-xinerama0 libxcb-xinput0\ 
    libxcb-image0 libxcb-keysyms1 libxcb-icccm4 libxcb-cursor0 libxcb-render-util0 \ 
    libxext6 libxrandr2 libqt5widgets5 libqt5gui5 libqt5core5a

# Install Flutter dependencies    
RUN apt-get install -y libmpv-dev libmpv2
RUN apt-get install -y gstreamer1.0-plugins-base
RUN ln -s /usr/lib/x86_64-linux-gnu/libmpv.so /usr/lib/libmpv.so.1

RUN apt-get install -y dos2unix

# Install curl, git, etc
RUN apt-get install -y curl git unzip xz-utils zip libglu1-mesa

# Copy requirements.txt to the working directory
COPY requirements.txt  /home/james/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Add local bin to PATH for user 'james'
ENV PATH="/home/james/.local/bin:$PATH"

# Set permissions for the working directory
RUN chown -R james:james /home/james
