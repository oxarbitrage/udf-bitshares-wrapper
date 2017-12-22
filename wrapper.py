from flask import Flask
from flask import jsonify
from flask import request

from websocket import create_connection
import json

import datetime
import time
import calendar

websocket_url = "ws://localhost:8090/ws"
ws = create_connection(websocket_url)

app = Flask(__name__)
from flask_cors import CORS, cross_origin
CORS(app)

# postgres
import psycopg2
postgres_host = 'localhost'
postgres_database = 'explorer'
postgres_username = 'postgres'
postgres_password = 'posta'
# end postgres


@app.route('/config')
def config():

    results = {}

    results["supports_search"] = True
    results["supports_group_request"] = False
    results["supported_resolutions"] = ["1", "5", "15", "30", "60", "240", "1D"]
    results["supports_marks"] = False
    results["supports_time"] = True

    return jsonify(results)

@app.route('/symbols')
def symbols():
    symbol = request.args.get('symbol')

    base,quote = symbol.split('_')

    ws.send('{"id":1, "method":"call", "params":[0,"lookup_asset_symbols",[["' + base + '"], 0]]}')
    result = ws.recv()
    j = json.loads(result)
    base_precision = 10**j["result"][0]["precision"]

    results = {}

    results["name"] = symbol
    results["ticker"] = symbol
    results["description"] = base + "/" + quote
    results["type"] = ""
    results["session"] = "24x7"
    results["exchange"] = ""
    results["listed_exchange"] = ""
    results["timezone"] = "Europe/London"
    results["minmov"] = 1
    results["pricescale"] = base_precision
    results["minmove2"] = 0
    results["fractional"] = False
    results["has_intraday"] = True
    results["supported_resolutions"] = ["1", "5", "15", "30", "60", "240", "1D"]
    results["intraday_multipliers"] = ""
    results["has_seconds"] = False
    results["seconds_multipliers"] = ""
    results["has_daily"] = True
    results["has_weekly_and_monthly"] = False
    results["has_empty_bars"] = True
    results["force_session_rebuild"] = ""
    results["has_no_volume"] = False
    results["volume_precision"] = ""
    results["data_status"] = ""
    results["expired"] = ""
    results["expiration_date"] = ""
    results["sector"] = ""
    results["industry"] = ""
    results["currency_code"] = ""

    return jsonify(results)


@app.route('/search')
def search():
    query = request.args.get('query')
    type = request.args.get('type')
    exchange = request.args.get('exchange')
    limit = request.args.get('limit')

    final = []

    con = psycopg2.connect(database=postgres_database, user=postgres_username, host=postgres_host,
                            password=postgres_password)
    cur = con.cursor()

    query = "SELECT * FROM markets WHERE pair LIKE '%" + query + "%'"
    #print query
    cur.execute(query)
    result = cur.fetchall()
    con.close()

    for w in range(0, len(result)):

        results = {}
        #print w
        base, quote = result[w][1].split('/')

        results["symbol"] = base + "_" + quote

        results["full_name"] = result[w][1]
        results["description"] = result[w][1]
        results["exchange"] = ""
        results["ticker"] = base + "_" + quote
        results["type"] = ""
        final.append(results)

    #print final
    return jsonify(final)

@app.route('/history')
def history():
    symbol = request.args.get('symbol')
    from_ = request.args.get('from')
    to = request.args.get('to')
    resolution = request.args.get('resolution')

    buckets = "86400"
    if resolution == "1":
        buckets = "60"
    elif resolution == "5":
        buckets = "300"
    elif resolution == "15":
        buckets = "900"
    elif resolution == "30":
        buckets = "1800"
    elif resolution == "60":
        buckets = "3600"
    elif resolution == "240":
        buckets = "14400"
    elif resolution == "1D":
        buckets = "86400"

    base, quote = symbol.split('_')

    results = {}

    ws.send('{"id":2,"method":"call","params":[1,"login",["",""]]}')
    login =  ws.recv()

    ws.send('{"id":2,"method":"call","params":[1,"history",[]]}')
    history =  ws.recv()
    history_j = json.loads(history)
    history_api = str(history_j["result"])

    ws.send('{"id":1, "method":"call", "params":[0,"lookup_asset_symbols",[["' + base + '"], 0]]}')
    result_l = ws.recv()
    j_l = json.loads(result_l)
    base_id = j_l["result"][0]["id"]
    base_precision = 10**j_l["result"][0]["precision"]

    ws.send('{"id":1, "method":"call", "params":[0,"lookup_asset_symbols",[["' + quote + '"], 0]]}')
    result_l = ws.recv()
    j_l = json.loads(result_l)
    quote_id = j_l["result"][0]["id"]
    quote_precision = 10**j_l["result"][0]["precision"]

    #print base_precision
    #print quote_precision

    left = datetime.datetime.fromtimestamp(int(from_)).strftime('%Y-%m-%dT%H:%M:%S')
    right = datetime.datetime.fromtimestamp(int(to)).strftime('%Y-%m-%dT%H:%M:%S')

    ws.send('{"id":1, "method":"call", "params":['+history_api+',"get_market_history", ["'+base_id+'", "'+quote_id+'", "'+buckets+'", "'+left+'", "'+right+'"]]}')

    result_l = ws.recv()

    j_l = json.loads(result_l)

    t = []
    c = []
    o = []
    h = []
    l = []
    v = []

    for w in range(0, len(j_l["result"])):

        open_quote = float(j_l["result"][w]["open_quote"])
        high_quote = float(j_l["result"][w]["high_quote"])
        low_quote = float(j_l["result"][w]["low_quote"])
        close_quote = float(j_l["result"][w]["close_quote"])
        close_quote = float(j_l["result"][w]["close_quote"])
        quote_volume = int(j_l["result"][w]["quote_volume"])

        open_base = float(j_l["result"][w]["open_base"])
        high_base = float(j_l["result"][w]["high_base"])
        low_base = float(j_l["result"][w]["low_base"])
        close_base = float(j_l["result"][w]["close_base"])
        base_volume = int(j_l["result"][w]["base_volume"])

        open = 1/(float(open_base/base_precision)/float(open_quote/quote_precision))
        high = 1/(float(high_base/base_precision)/float(high_quote/quote_precision))
        low = 1/(float(low_base/base_precision)/float(low_quote/quote_precision))
        close = 1/(float(close_base/base_precision)/float(close_quote/quote_precision))
        volume = quote_volume

        c.append(close)
        o.append(open)
        h.append(high)
        l.append(low)
        v.append(volume)

        date = datetime.datetime.strptime(j_l["result"][w]["key"]["open"], "%Y-%m-%dT%H:%M:%S")
        ts = calendar.timegm(date.utctimetuple())
        t.append(ts)


    len_result = len(j_l["result"])
    counter = 0
    while len_result == 200:

        counter = counter + 200

        left = datetime.datetime.fromtimestamp(int(t[-1]+1)).strftime('%Y-%m-%dT%H:%M:%S')
        ws.send('{"id":1, "method":"call", "params":[' + history_api + ',"get_market_history", ["' + base_id + '", "' + quote_id + '", "' + buckets + '", "' + left + '", "' + right + '"]]}')

        result = ws.recv()
        j_l = json.loads(result)

        len_result = len(j_l["result"])

        for w in range(0, len(j_l["result"])):

            open_quote = float(j_l["result"][w]["open_quote"])
            high_quote = float(j_l["result"][w]["high_quote"])
            low_quote = float(j_l["result"][w]["low_quote"])
            close_quote = float(j_l["result"][w]["close_quote"])
            quote_volume = int(j_l["result"][w]["quote_volume"])

            open_base = float(j_l["result"][w]["open_base"])
            high_base = float(j_l["result"][w]["high_base"])
            low_base = float(j_l["result"][w]["low_base"])
            close_base = float(j_l["result"][w]["close_base"])
            base_volume = int(j_l["result"][w]["base_volume"])

            open = 1/(float(open_base / base_precision) / float(open_quote / quote_precision))
            high = 1/(float(high_base / base_precision) / float(high_quote / quote_precision))
            low = 1/(float(low_base / base_precision) / float(low_quote / quote_precision))
            close = 1/(float(close_base / base_precision) / float(close_quote / quote_precision))
            volume = quote_volume

            c.append(close)
            o.append(open)
            h.append(high)
            l.append(low)
            v.append(volume)

            date = datetime.datetime.strptime(j_l["result"][w]["key"]["open"], "%Y-%m-%dT%H:%M:%S")
            ts = calendar.timegm(date.utctimetuple())
            t.append(ts)

    results["s"] = "ok"
    results["t"] = t
    results["c"] = c
    results["o"] = o
    results["h"] = h
    results["l"] = l
    results["v"] = v

    #results["v"] = ""

    # if s = error ; results["errmsg"] = "Some eror msg here"

    return jsonify(results)

@app.route('/time')
def time():

    ws.send('{"id":1, "method":"call", "params":[0,"get_dynamic_global_properties",[]]}')
    result = ws.recv()
    j = json.loads(result)

    date = datetime.datetime.strptime(j["result"]["time"], "%Y-%m-%dT%H:%M:%S")
    return jsonify(str(calendar.timegm(date.utctimetuple())))
