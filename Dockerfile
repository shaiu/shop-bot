FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY src ./

ENV PYTHONPATH=/usr/src/app/shop-bot:/usr/src/app

EXPOSE 5000

CMD [ "python", "./shop-bot/bot.py" ]