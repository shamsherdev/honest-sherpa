FROM python:3.6-stretch
RUN python -m pip install --upgrade pip
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
RUN python manage.py migrate