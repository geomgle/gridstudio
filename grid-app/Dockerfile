FROM ubuntu:20.04 as base

ARG GIT_TOKEN

# make clear that it is a noninteractive session
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt clean && \
apt update && \
apt install -y \
software-properties-common \
build-essential \
wget \
python3-pip \
locales \
curl \
git

# # TODO: see if any locale issues arise
# # RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
# #     locale-gen
# # ENV LANG en_US.UTF-8  
# # ENV LANGUAGE en_US:en  
# # ENV LC_ALL en_US.UTF-8  

# Install Python3.7 from ppa (for fast speed)
RUN add-apt-repository ppa:deadsnakes/ppa && \
apt update && \
apt install -y \
    python3.7 \
    python3.7-distutils

# copy over all files to /home/source/
WORKDIR /home/source/
COPY . /home/source/

# install python + dependencies + nodejs
# apt install -y python3-tk && \
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
apt install -y nodejs

# RUN python3.7 -m pip install --upgrade pip numpy pandas matplotlib scipy scikit-learn

RUN git clone https://$GIT_TOKEN@github.com/geomgle/.dotfiles /root/.dotfiles

# python3.7 -m pip install tensorflow

# TODO: think about how to run terminal-server, probably multiple terminal-servers with parameters (one for each workspace)
# create /home/run/ directory to run terminal nodejs project from
RUN mkdir /home/run/
COPY ./terminal-server/ /home/run/terminal-server/

# install required NPM packages for term.js
WORKDIR /home/run/terminal-server/
RUN npm install --no-cache

# create work directory
RUN mkdir /home/user/

# set working directory to source to install go dependencies
WORKDIR /home/source/

RUN wget https://go.dev/dl/go1.18.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.18.linux* && \
    rm go1.18.linux-amd64.tar.gz
ENV PATH /usr/local/go/bin:${PATH}

# RUN go get -d -v ./...

#
# build manager.go once to speed up consecutive go builds
# WORKDIR /home/source/proxy/
# RUN go build manager.go
# RUN rm ./manager
#
# # expose ports
# EXPOSE 8080
#
# WORKDIR /home/source/proxy/
#
# CMD ["bash","run-manager-proxy.sh"]
