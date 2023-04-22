# Shopping list

A telegram bot that you can add items to your cart on the go.

** Currently only works with https://www.rami-levy.co.il/he/online/market

## Installation

### Step 1

#### Create a telegram bot

To create a chatbot on Telegram, you need to contact the BotFather, which is essentially a bot used to create other
bots.

The command you need is /newbot which leads to the following steps to create your bot:

Your bot should have two attributes: a name and a username. The name will show up for your bot, while the username will
be used for mentions and sharing.

After choosing your bot name and username—which must end with “bot”—you will get a message containing your access token,
and you’ll obviously need to save your access token and username for later, as you will be needing them.

### Step 2

#### Setup environment variables

Before we can go and set up the container using docker command or docker-compose we need to setup environment variables.

`ECOMTOKEN`

`PORT`

`RAMY_USER`

`RAMY_PASS`

`STORE`

`TELEGRAM_BOT_TOKEN`

`WEBHOOK_URL`

#### Docker compose

After saving then environment variables in file, create the following docker-compose file:

```
version: "3.7"

services:

  shop:
    image: shaiungar/shopping-list:main
    container_name: shop
    restart: always
    ports:
      - "5000:5000"
    env_file:
      - .env
```

Now, run the following command to install and start the bot:

```
docker-compose up -d
```