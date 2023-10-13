FROM ubuntu:latest as base

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

RUN apt install -y \
      libpq-dev 
# # TODO: see if any locale issues arise
# # RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
# #     locale-gen
# # ENV LANG en_US.UTF-8  
# # ENV LANGUAGE en_US:en  
# # ENV LC_ALL en_US.UTF-8  

RUN apt install -y \
      python3.10 
RUN python3.10 -m pip install --upgrade pip numpy pandas matplotlib scipy scikit-learn

# Install nvm with node and npm
ENV NVM_DIR /root/.nvm
ENV NODE_VERSION 16.20.2
RUN curl https://raw.githubusercontent.com/creationix/nvm/v0.39.5/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default
ENV NODE_PATH $NVM_DIR/versions/node/v$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

# install go
RUN wget https://go.dev/dl/go1.18.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.18.linux* && \
    rm go1.18.linux-amd64.tar.gz
ENV PATH /usr/local/go/bin:${PATH}

# install .dotfiles
RUN git clone https://$GIT_TOKEN@github.com/geomgle/.dotfiles /root/.dotfiles

# copy over all files to /home/source/
WORKDIR /home/source/
COPY . /home/source/

# TODO: think about how to run terminal-server, probably multiple terminal-servers with parameters (one for each workspace)
# create /home/run/ directory to run terminal nodejs project from
RUN mkdir /home/run/
COPY ./terminal-server/ /home/run/terminal-server/

# install required NPM packages for term.js
# python3.11 makes errors: 
#   npm config set python /usr/bin/python3.10
WORKDIR /home/run/terminal-server/
RUN npm install --no-cache

# create work directory
RUN mkdir /home/user/

# set working directory to source to install go dependencies
WORKDIR /home/source/
RUN go install

# build manager.go once to speed up consecutive go builds
WORKDIR /home/source/proxy/
RUN go install

# expose ports
EXPOSE 8080

WORKDIR /home/source/proxy/

CMD ["bash","run-manager-proxy.sh"]
