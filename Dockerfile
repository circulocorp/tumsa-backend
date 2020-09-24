FROM python:2.7
COPY . /app
WORKDIR /app
#RUN apk update && apk add postgresql-dev gcc python2-dev musl-dev
RUN apt-get install gcc
RUN pip install -r requirements.txt
ENV ENVIRONMENT=dev
CMD python ./main.py