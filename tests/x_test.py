import pprint
from unittest import TestCase
import json
import re
import ast


def test():
    result = '''{
        "ret_code": 0,
        "ret_msg": "OK",
        "ext_code": "",
        "ext_info": "",
        "result": {
            "user_id": 1,
            "order_id": "335fd977-e5a5-4781-b6d0-c772d5bfb95b",
            "symbol": "BTCUSD",
            "side": "Buy",
            "order_type": "Market",
            "price": 8800,
            "qty": 1,
            "time_in_force": "GoodTillCancel",
            "order_status": "Created",
            "last_exec_time": 0,
            "last_exec_price": 0,
            "leaves_qty": 1,
            "cum_exec_qty": 0,
            "cum_exec_value": 0,
            "cum_exec_fee": 0,
            "reject_reason": "",
            "order_link_id": "",
            "created_at": "2019-11-30T11:03:43.452Z",
            "updated_at": "2019-11-30T11:03:43.455Z"
        },
        "time_now": "1575111823.458705",
        "rate_limit_status": 98,
        "rate_limit_reset_ms": 1580885703683,
        "rate_limit": 100
    }'''

    data = json.loads(result)
    a = {key: value for (key, value) in data['result'].items() if key == "price"}
    return a


class XTest(TestCase):
    def test_isNone(self):
        self.assertIsNone(test())

    def test_isDict(self):
        self.assertIsInstance(test(), dict)

