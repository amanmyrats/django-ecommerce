# pull official base image
# FROM python:3.9.6-alpine
FROM ubuntu:20.04

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install packages
# RUN apk update \
#     && apk add postgresql-dev gcc python3-dev py3-setuptools musl-dev
# RUN apk add tiff-dev jpeg-dev openjpeg-dev zlib-dev freetype-dev lcms2-dev \
#     libwebp-dev tcl-dev tk-dev harfbuzz-dev fribidi-dev libimagequant-dev \
#     libxcb-dev libpng-dev
RUN apt-get update \
    && install -y python3-dev python3-setuptools \
    && install -y python-dev \
    && install -y libjpeg-dev \
    && install -y libjpeg8-dev \
    && install -y libpng3

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]