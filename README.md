# The bitshares udf wrapper

UDF protocol is needed to build DEX market charts with TradingView.

This wrapper will expose an udf API set by calling a bitshares witness node with `market_history` plugin enabled to get data from the dex.

## Online demo

http://open-explorer.io/tradingview/

## Install dependencies

Currently the UDF wrapper needs a postgres database with assets. This is done by having https://github.com/oxarbitrage/bitshares-python-api-backend installed.
All dependencies needed for this project are covered by having `bitshares-python-api-backend`. It is expected this to change in the future and being a totally standalone project.

## Basic run:

```
git clone https://github.com/oxarbitrage/udf-bitshares-wrapper.git
export FLASK_APP=wrapper.py
flask run --host=0.0.0.0 --port=5001
```

Or by having nginx:

```
#vi /etc/nginx/sites-available/udf
server {
    listen 5001;
    server_name 23.94.69.140;
    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/udf.sock;
    }
}
#ln -s /etc/nginx/sites-available/udf /etc/nginx/sites-enabled/udf
#/etc/init.d/nginx restart
```

And then in the root of the project start with:

`uwsgi --ini wrapper.ini`

## API Calls

The following calls are exposed and needed for TradingView to display bitshares dex charts:

- `/config` -  http://23.94.69.140:5001/config

- `/symbols` - http://23.94.69.140:5001/symbols?symbol=BTS_USD

- `/history` - http://23.94.69.140:5001/history?symbol=BTS_USD&resolution=D&from=1513092731&to=1513956731

- `/search` - http://23.94.69.140:5001/search?limit=30&query=BLOCK&type=&exchange=

- `/time` - http://23.94.69.140:5001/time

## Api docs:

http://23.94.69.140:5001/
