from emx.rest_api import RestApi
from emx.ws_api import WebSocketApi
from emx.utils import EmxApiException
import asyncio

import sys
import json

 # params
spread = 10
apikey = 'api-key'
apisecret = 'api-secret'

contract_code = 'BTC-PERP'

def ws_api_examples():
    api = WebSocketApi(apikey, apisecret)
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
                        if side == "buy":
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
    ws_api_examples()
