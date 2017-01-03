#-*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

"""
test_turbo_motor
----------------------------------

Tests for `model` module.
"""

import os
import sys
import datetime
import json
import StringIO
import inspect
import unittest

from bson.objectid import ObjectId
from pymongo import (
    results as mongo_results,
    MongoClient
)
from tornado.testing import gen_test, AsyncTestCase
from tornado import gen
from motor import motor_tornado
import motor
from turbo_motor.model import BaseModel
from util import fake_ids, fake_ids_2

os.environ['ASYNC_TEST_TIMEOUT'] = '10'


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

    def write_action_call(self, name, *args, **kwargs):
        pass


class BaseModelTest(AsyncTestCase):

    def setUp(self):
        # Stray StopIteration exceptions can lead to tests exiting prematurely,
        # so we need explicit checks here to make sure the tests run all
        # the way through.
        super(BaseModelTest, self).setUp()
        mc = motor.MotorClient()
        db = {
            'db': {'test': mc['test']},
            'db_file': {'test': None}
        }
        self.tb_tag = Tag('test', db)
        self.mc = mc
        self._make_data()

    def tearDown(self):
        super(BaseModelTest, self).tearDown()
        del self.tb_tag
        self._clean_data()

    def _make_data(self):
        tb_tag = MongoClient()['test']['tag']
        for i in fake_ids:
            tb_tag.insert_one({'_id': i})

    def _clean_data(self):
        tb_tag = MongoClient()['test']['tag']
        for i in fake_ids:
            tb_tag.delete_one({'_id': i})
        for i in fake_ids_2:
            tb_tag.delete_one({'_id': i})

    @gen_test
    def test_insert(self):
        _id = yield self.tb_tag.insert({'_id': fake_ids_2[0]})
        self.assertIsNot(_id, fake_ids_2[0])

    @gen_test
    def test_insert_one(self):
        result = yield self.tb_tag.insert_one({'_id': fake_ids_2[0]})
        self.assertIsInstance(result, mongo_results.InsertOneResult)

    @gen_test
    def test_find_one(self):
        result = yield self.tb_tag.find_one()
        self.assertIsNot(result, None)

    @gen_test
    def test_find_one_with_wrapper(self):
        # test find_one default wrapper=False
        with self.assertRaises(KeyError):
            result = yield self.tb_tag.find_one(wrapper=False)
            result['nokey']

        _id = yield self.tb_tag.insert({'_id': fake_ids_2[0]})
        result = yield self.tb_tag.find_one({'_id': _id}, wrapper=True)
        self.assertEqual(result['key'], None)

    @gen_test
    def test_find_by_id(self):
        result = yield self.tb_tag.find_by_id(fake_ids[0])
        self.assertEqual(result['_id'], fake_ids[0])

        result = yield self.tb_tag.find_by_id(fake_ids[0:10])
        for index, i in enumerate(result):
            self.assertEqual(i['_id'], fake_ids[0:10][index])

    @gen_test
    def test_update(self):
        with self.assertRaises(ValueError):
            yield self.tb_tag.update({}, {'hello': 0})

        yield self.tb_tag.update({}, {'$set': {'hello': 0}})

        with self.assertRaises(ValueError):
            yield self.tb_tag.update({}, {})

    @gen_test
    def test_remove(self):
        with self.assertRaises(Exception):
            yield self.tb_tag.remove({})

        result = yield self.tb_tag.find_by_id(fake_ids[0])
        self.assertEqual(result['_id'], fake_ids[0])

        yield self.tb_tag.remove({'_id': fake_ids[0]})
        result = yield self.tb_tag.find_by_id(fake_ids[0])
        self.assertEqual(result, None)

    @gen_test
    def test_remove_by_id(self):
        result = yield self.tb_tag.remove_by_id(fake_ids[0])
        self.assertEqual(result.deleted_count, 1)

        result = yield self.tb_tag.remove_by_id(fake_ids[1:10])
        for index, i in enumerate(result):
            self.assertEqual(i.deleted_count, 1)

    @gen_test
    def test_create(self):
        with self.assertRaises(Exception):
            result = yield self.tb_tag.create({'nokey': 10})
        _id = yield self.tb_tag.create({'imgid': None})
        self.assertIsNot(_id, None)
        result = yield self.tb_tag.find_by_id(_id)
        self.assertEqual(result['value'], 0)
        self.tb_tag.remove_by_id(_id)

    @gen_test
    def test_inc(self):
        _id = yield self.tb_tag.insert({'value': 10})
        yield self.tb_tag.inc({'_id': _id}, 'value')
        result = yield self.tb_tag.find_by_id(_id)
        self.assertEqual(result['value'], 11)
        yield self.tb_tag.remove_by_id(_id)

    # def test_find_wrapper(self):
    #     # test find wrapper=True return generator
    #     one = self.m.find_one()
    #     with self.assertRaises(KeyError):
    #         one['keyerror']

    #     one = self.m.find_one(wrapper=True)
    #     self.assertEqual(one['keyerror'], None)

    #     for one in self.m.find(limit=5):
    #         with self.assertRaises(KeyError):
    #             one['keyerror']

    #     for one in self.m.find(limit=5, wrapper=True):
    #         self.assertEqual(one['keyerror'], None)


if __name__ == '__main__':
    unittest.main()
