# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath('..'))

from turbo_motor.model import BaseModel


TEST_MODULES = [
    'model_test',
]


def main():
    testSuite = unittest.TestSuite()
    for module in TEST_MODULES:
        suite = unittest.TestLoader().loadTestsFromName(module)
        testSuite.addTest(suite)

    return testSuite


def main2():
    import datetime
    from bson.objectid import ObjectId
    import motor
    from util import start_loop, stop_loop
    from motor.motor_tornado import MotorClient

    def fetch_coroutine_callback(future):
        print('coroutine callback')
        print(future.result())
        stop_loop()

    class Tag(BaseModel):
        name = 'tag'
        field = {
            'list': (list, []),
            'imgid': (ObjectId, None),
            'uid': (ObjectId, None),
            'name': (basestring, None),
            'value': (int, 0),
            'atime': (datetime.datetime, None),
            'up': (dict, {}),
        }

        def __init__(self):
            # mc = motor.MotorClient()
            mc = MotorClient()
            db = {
                'db': {'test': mc['test']},
                'db_file': {'test': None}
            }
            super(Tag, self).__init__('test', db)

        def write_action_call(self, name, *args, **kwargs):
            pass

    tag = Tag()
    futrue = tag.insert({'value': 10})
    futrue.add_done_callback(fetch_coroutine_callback)
    start_loop()


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(main())
    # main2()
