FROM python:3

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/shop-bot:/app

EXPOSE 5000

CMD [ "python", "./shop-bot/bot.py" ]