# The bitshares udf wrapper

UDF protocol is needed to build DEX market charts with TradingView.

This wrapper will expose udf calls y calling a bitshares witness node to get data from the dex.

## Online demo

http://open-explorer.io/tradingview/


## Basic run:
```
git clone https://github.com/oxarbitrage/bitshares-udf-wrapper.git
export FLASK_APP=wrapper.py
flask run --host=0.0.0.0 --port=5001
```

## API Calls

http://23.94.69.140:5001/config

http://23.94.69.140:5001/symbols?symbol=BTS_USD

http://23.94.69.140:5001/history?symbol=BTS_USD&resolution=D&from=1513092731&to=1513956731

http://23.94.69.140:5001/search?limit=30&query=BLOCK&type=&exchange=

http://23.94.69.140:5001/time




