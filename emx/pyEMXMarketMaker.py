from emx.rest_api import RestApi
from emx.ws_api import WebSocketApi
from emx.utils import EmxApiException

import sys
import json

 # params
avPrice = 9700
bands = 10
spread = 10
size = '0.0002'
stopOffset = 2500
api = RestApi('api-key', 'api-secret')

stopPrice =  avPrice - ( bands * spread ) - stopOffset 

contract_code = 'BTC-PERP'

def rest_api_examples():
    try:
        res = api.get_account()
       
        order_type = 'limit'
        order_side = 'buy'
        # set orders
        count = 0
        while count < bands:
            count = count + 1
            price = avPrice - count * spread 
            # print(price)
            api.create_new_order(contract_code, order_type, order_side, size, "", str(price))
        # set stop
        sizeStop = float(size) * bands
        api.create_new_order( contract_code, "stop_limit", "sell", str( sizeStop ), "", str( stopPrice ))


    except EmxApiException as err:
        print(err)
    except Exception as err:
        print("Exception raised: {}".format(err))
    else:
        print(res)


def ws_api_examples():
    api = WebSocketApi('api-key', 'api-secret')
    channels = ["orders", "trading"]
    api.subscribe(["BTC-PERP"], channels)

    while True:
        try:
            res = json.loads(api.receive_msg())
            # print(res)
            if "channel" in res:
                if res["channel"] == "orders" and res["type"] == "update" and res["action"] == "filled":
                    dat = res["data"]
                    if dat["status"] == "done":
                        side = dat["side"]
                        price = dat["price"]
                        size = dat["size"]
                        if dat["order_type"] == "stop_market":
                            msg = {
                                "channel": "trading",
                                "type": "request",
                                "action": "cancel-all-orders",
                                "data": {
                                    "contract_code": "BTC-PERP"
                                }
                            }
                            api.ws.send(json.dumps(msg))
                            sys.exit()
                        elif side == "buy":
                            # set sell order
                            fprice = float( price )
                            sellPrice = fprice + spread
                            msg =  {
                                "channel": "trading",
                                "type": "request",
                                "action": "create-order",
                                "data": {
                                    "contract_code": "BTC-PERP",
                                    "client_id": "",
                                    "type": "limit",
                                    "side": "sell",
                                    "size": size,
                                    "price": str( sellPrice )
                                }   
                            }
                            api.ws.send(json.dumps(msg))
                        elif side == "sell":
                            # set buy order
                            fprice = float( price )
                            buyPrice = fprice -  spread
                            msg =  {
                                "channel": "trading",
                                "type": "request",
                                "action": "create-order",
                                "data": {
                                    "contract_code": "BTC-PERP",
                                    "client_id": "",
                                    "type": "limit",
                                    "side": "buy",
                                    "size": size,
                                    "price": str( buyPrice )
                                }   
                            }
                            api.ws.send(json.dumps(msg))
    
        except EmxApiException as err:
            print(err)
            ws_api_examples()
        except Exception as err:
            print("Exception raised: {}".format(err))
            break


if __name__ == "__main__":
    rest_api_examples()
    ws_api_examples()
