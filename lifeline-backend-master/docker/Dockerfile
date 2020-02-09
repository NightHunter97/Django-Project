FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /lifeline
WORKDIR /lifeline
ADD requirements.txt /lifeline/
RUN pip install --default-timeout=100 -r requirements.txt
ADD . /lifeline/
RUN chmod +x /lifeline/docker/start.sh

CMD ["/lifeline/docker/start.sh"]
