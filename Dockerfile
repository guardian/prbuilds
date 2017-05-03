FROM java:openjdk-8

RUN apt-get update
RUN apt-get install -y sudo wget screen python-setuptools vim
RUN easy_install pip
RUN pip install awscli
RUN useradd -ms /bin/bash ubuntu
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

COPY ./trousers/ /home/ubuntu/prbuilds/trousers/
COPY ./ether/ /home/ubuntu/prbuilds/ether/
COPY ./install.sh /home/ubuntu/prbuilds/
RUN chown ubuntu -R /home/ubuntu/prbuilds

USER ubuntu
WORKDIR /home/ubuntu/prbuilds
CMD ["./install.sh", "-test"]
