FROM debian:wheezy

RUN set -ex; \
    apt-get update -qq; \
    apt-get install -y \
        python \
        python-pip \
        python-dev \
        git \
        apt-transport-https \
        ca-certificates \
        curl \
        lxc \
        iptables \
    ; \
    rm -rf /var/lib/apt/lists/*

ENV ALL_DOCKER_VERSIONS 1.6.0-rc4

RUN set -ex; \
    curl https://test.docker.com/builds/Linux/x86_64/docker-1.6.0-rc4 -o /usr/local/bin/docker-1.6.0-rc4; \
    chmod +x /usr/local/bin/docker-1.6.0-rc4

# Set the default Docker to be run
RUN ln -s /usr/local/bin/docker-1.6.0-rc4 /usr/local/bin/docker

RUN useradd -d /home/user -m -s /bin/bash user
WORKDIR /code/

ADD requirements.txt /code/
RUN pip install -r requirements.txt

ADD requirements-dev-py2.txt /code/
RUN pip install -r requirements-dev-py2.txt

ADD . /code/
RUN python setup.py install

RUN chown -R user /code/

ENTRYPOINT ["/usr/local/bin/docker-compose"]
