FROM ubuntu:trusty

RUN useradd -d /home/user -m -s /bin/bash user

RUN set -x \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
        software-properties-common \
 && add-apt-repository -y ppa:fkrull/deadsnakes \
 && apt-get update -qq \
 && DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
        python \
        python2.6 \
        python2.7 \
        python3.3 \
        python3.4 \
        pypy \
        git \
        apt-transport-https \
        ca-certificates \
        curl \
        lxc \
        iptables \
 && rm -rf /var/lib/apt/lists/* \
 && curl -SsL 'https://bootstrap.pypa.io/get-pip.py' | python

# ENV ALL_DOCKER_VERSIONS 1.6.0

# RUN set -ex; \
#     for v in ${ALL_DOCKER_VERSIONS}; do \
#         curl -Ss https://get.docker.com/builds/Linux/x86_64/docker-$v -o /usr/local/bin/docker-$v; \
#         chmod +x /usr/local/bin/docker-$v; \
#     done

# Temporarily use dev version of Docker
ENV ALL_DOCKER_VERSIONS dev
RUN curl -Ss https://master.dockerproject.com/linux/amd64/docker-1.5.0-dev > /usr/local/bin/docker-dev
RUN chmod +x /usr/local/bin/docker-dev

WORKDIR /code
ADD requirements*.txt tox.ini ./
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
RUN tox --notest

ADD . ./
RUN python setup.py install

RUN chown -R user /code/

ENTRYPOINT ["/usr/local/bin/docker-compose"]
