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

ENV ALL_DOCKER_VERSIONS 1.3.3 1.4.1 1.5.0 1.6.0-rc2

 RUN set -ex; \
     for v in 1.3.3 1.4.1 1.5.0; do \
         curl -Ss https://get.docker.com/builds/Linux/x86_64/docker-$v -o /usr/local/bin/docker-$v; \
         chmod +x /usr/local/bin/docker-$v; \
     done; \
     curl -Ss https://test.docker.com/builds/Linux/x86_64/docker-1.6.0-rc2 -o /usr/local/bin/docker-1.6.0-rc2; \
     chmod +x /usr/local/bin/docker-1.6.0-rc2

# Set the default Docker to be run
RUN ln -s /usr/local/bin/docker-1.3.3 /usr/local/bin/docker

WORKDIR /code
ADD requirements*.txt tox.ini ./
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
RUN tox --notest

ADD . ./
RUN python setup.py install

RUN chown -R user /code/

ENTRYPOINT ["/usr/local/bin/docker-compose"]
