FROM python:3.9.5-alpine3.13

RUN echo -e "http://nl.alpinelinux.org/alpine/v3.5/main\nhttp://nl.alpinelinux.org/alpine/v3.5/community" > /etc/apk/repositories

RUN apk upgrade

RUN apk add git

WORKDIR /assets

COPY requirements.txt .

RUN pip install --no-cache-dir --user -U -r requirements.txt

COPY / .

CMD [ "python", "main.py"]
