# -*- coding: utf-8 -*-
from __future__ import (
    absolute_import,
    division,
    print_function,
    with_statement,
)

from tornado import gen
from pymongo import DESCENDING
from bson.objectid import ObjectId
from motor.motor_tornado import MotorCollection
from turbo.mongo_model import (
    AbstractModel,
    _record,
)


class BaseBaseModel(AbstractModel):
    """class implement almost all mongodb collection method
    """
    PRIMARY_KEY_TYPE = ObjectId

    def __init__(self, db_name='test', _MONGO_DB_MAPPING=None):
        self.__collect, self.__gridfs = super(
            BaseBaseModel, self)._init(db_name, _MONGO_DB_MAPPING)

    def _to_primary_key(self, _id):
        if self.PRIMARY_KEY_TYPE is ObjectId:
            return self.to_objectid(_id)

        return _id

    def __getattr__(self, k):
        attr = getattr(self.__collect, k)
        if isinstance(attr, MotorCollection):
            raise AttributeError("model object '%s' has not attribute '%s'" % (self.name, k))
        return attr

    def sub_collection(self, name):
        return self.__collect[name]

    @gen.coroutine
    def insert(self, doc_or_docs, **kwargs):
        """
        return
            insert doc _id backwards compatibility
        """
        result = yield self.__collect.insert_one(doc_or_docs, **kwargs)
        raise gen.Return(self._to_primary_key(result.inserted_id))

    @gen.coroutine
    def insert_one(self, doc_or_docs, **kwargs):
        result = yield self.__collect.insert_one(doc_or_docs, **kwargs)
        raise gen.Return(result)

    @gen.coroutine
    def find_one(self, spec_or_id=None, *args, **kwargs):
        """
        :args
            wrapper wrap result to _record or not

        """
        wrapper = kwargs.pop('wrapper', False)
        result = yield self.__collect.find_one(spec_or_id, *args, **kwargs)
        if wrapper is True:
            raise gen.Return(_record(result))

        raise gen.Return(result)

    # @gen.coroutine
    # def find(self, *args, **kwargs):
    #     """collection find method
    #     http://stackoverflow.com/questions/33482066/using-regular-python-generator-in-tornado-coroutine
    #     """
    #     queue = kwargs.pop('queue', None)
    #     cursor = self.__collect.find(*args, **kwargs)
    #     while (yield cursor.fetch_next):
    #         doc = cursor.next_object()
    #         queue.put(doc)

    @gen.coroutine
    def update(self, spec, document, multi=False, **kwargs):
        """update method
        """
        for opk in document.keys():
            if not opk.startswith('$') or opk not in self._operators:
                raise ValueError("invalid document update operator")

        if not document:
            raise ValueError("empty document update not allowed")

        result = yield self.__collect.update(spec, document, multi=multi, **kwargs)
        raise gen.Return(result)

    @gen.coroutine
    def remove(self, spec_or_id=None, **kwargs):
        """collection remove method
        warning:
            if you want to remove all documents,
            you must override _remove_all method to make sure
            you understand the result what you do
        """
        if isinstance(spec_or_id, dict) and spec_or_id == {}:
            raise ValueError("not allowed remove all documents")

        if spec_or_id is None:
            raise ValueError("not allowed remove all documents")

        result = yield self.__collect.delete_one(spec_or_id, **kwargs)
        raise gen.Return(result)

    # def put(self, value, **kwargs):
    #     if value:
    #         return self.__gridfs.put(value, **kwargs)
    #     return None

    # def delete(self, _id):
    #     return self.__gridfs.delete(self.to_objectid(_id))

    # def get(self, _id):
    #     return self.__gridfs.get(self.to_objectid(_id))

    # def read(self, _id):
    #     return self.__gridfs.get(self.to_objectid(_id)).read()

    @gen.coroutine
    def find_by_id(self, _id, column=None):
        """find record by _id
        """
        if isinstance(_id, list) or isinstance(_id, tuple):
            as_list = []
            for i in _id:
                result = yield self.__collect.find_one(
                    {'_id': self._to_primary_key(i)}, column)
                as_list.append(result)
            raise gen.Return(as_list)

        document_id = self._to_primary_key(_id)

        if document_id is None:
            raise gen.Return(None)

        result = yield self.__collect.find_one({'_id': document_id}, column)
        raise gen.Return(result)

    @gen.coroutine
    def remove_by_id(self, _id):
        if isinstance(_id, list) or isinstance(_id, tuple):
            as_list = []
            for i in _id:
                result = yield self.__collect.delete_one(
                    {'_id': self._to_primary_key(i)})
                as_list.append(result)
            raise gen.Return(as_list)

        result = yield self.__collect.delete_one(
            {'_id': self._to_primary_key(_id)})
        raise gen.Return(result)

    # @gen.coroutine
    # def find_new_one(self, *args, **kwargs):
    #     cur = list(self.__collect.find(*args, **kwargs).limit(1).sort('_id', DESCENDING))
    #     if cur:
    #         return cur[0]

    #     return None

    # def get_as_column(self, condition=None, column=None, skip=0, limit=0, sort=None):
    #     if column is None:
    #         column = self.column

    #     return self.find(condition, column, skip=skip, limit=limit, sort=sort)

    # def get_as_dict(self, condition=None, column=None, skip=0, limit=0, sort=None):
    #     if column is None:
    #         column = self.column

    #     as_list = self.__collect.find(condition, column, skip=skip, limit=limit, sort=sort)

    #     as_dict, as_list = {}, []
    #     for i in as_list:
    #         as_dict[str(i['_id'])] = i
    #         as_list.append(i)

    #     return as_dict, as_list

    @gen.coroutine
    def create(self, record=None, **args):
        """Init the new record with field dict
        """
        if isinstance(record, list) or isinstance(record, tuple):
            record = [self._valid_record(i) for i in record]

        if isinstance(record, dict):
            record = self._valid_record(record)

        result = yield self.insert(record, **args)
        raise gen.Return(result)

    @gen.coroutine
    def inc(self, spec_or_id, key, num=1):
        result = yield self.__collect.update_one(spec_or_id, {'$inc': {key: num}})
        raise gen.Return(result)


class BaseModel(BaseBaseModel):
    pass
