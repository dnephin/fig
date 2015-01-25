FROM debian:wheezy
RUN apt-get update -qq && apt-get install -qy python python-pip python-dev git && apt-get clean
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
