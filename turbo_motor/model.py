# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import with_statement

from motor.motor_tornado import MotorCollection
from pymongo import DESCENDING
from tornado import gen
from turbo.mongo_model import _record
from turbo.mongo_model import AbstractModel


class BaseBaseModel(AbstractModel):
    """class implement almost all mongodb collection method
    """

    def __init__(self, db_name='test', _MONGO_DB_MAPPING=None):
        self.__collect, self.__gridfs = super(
            BaseBaseModel, self)._init(db_name, _MONGO_DB_MAPPING)

    def __getattr__(self, k):
        attr = getattr(self.__collect, k)
        if isinstance(attr, MotorCollection):
            raise AttributeError(
                "model object '%s' has not attribute '%s'" % (self.name, k))
        return attr

    def sub_collection(self, name):
        return self.__collect[name]

    @gen.coroutine
    def insert(self, doc_or_docs, **kwargs):
        """
        return:
            insert doc _id backwards compatibility
        """
        check = kwargs.pop('check', True)
        if isinstance(doc_or_docs, dict):
            if check is True:
                doc_or_docs = self._valid_record(doc_or_docs)
            result = yield self.__collect.insert_one(doc_or_docs, **kwargs)
            raise gen.Return(self._to_primary_key(result.inserted_id))
        else:
            if check is True:
                for d in doc_or_docs:
                    d = self._valid_record(d)
            result = yield self.__collect.insert_many(doc_or_docs, **kwargs)
            raise gen.Return(result.inserted_ids)

    @gen.coroutine
    def save(self, to_save, **kwargs):
        """save method
        """
        self._valid_record(to_save)
        if '_id' in to_save:
            yield self.__collect.replace_one(
                {'_id': to_save['_id']}, to_save, **kwargs)
            raise gen.Return(to_save['_id'])
        else:
            result = yield self.__collect.insert_one(to_save, **kwargs)
            raise gen.Return(self._to_primary_key(result.inserted_id))

    @gen.coroutine
    def update(self, filter_, document, multi=False, **kwargs):
        """update method
        """
        self._valide_update_document(document)
        if multi:
            result = yield self.__collect.update_many(
                filter_, document, **kwargs)
        else:
            result = yield self.__collect.update_one(
                filter_, document, **kwargs
            )
        raise gen.Return(result)

    @gen.coroutine
    def remove(self, filter_=None, **kwargs):
        """collection remove method
        warning:
            if you want to remove all documents,
            you must override _remove_all method to make sure
            you understand the result what you do
        """
        if isinstance(filter_, dict) and filter_ == {}:
            raise ValueError("not allowed remove all documents")

        if filter_ is None:
            raise ValueError("not allowed remove all documents")

        if kwargs.pop('multi', False) is True:
            result = yield self.__collect.delete_many(filter_, **kwargs)
        else:
            result = yield self.__collect.delete_one(filter_, **kwargs)

        raise gen.Return(result)

    @gen.coroutine
    def insert_one(self, doc_or_docs, **kwargs):
        check = kwargs.pop('check', True)
        if check is True:
            self._valid_record(doc_or_docs)
        result = yield self.__collect.insert_one(doc_or_docs, **kwargs)
        raise gen.Return(result)

    @gen.coroutine
    def insert_many(self, doc_or_docs, **kwargs):
        check = kwargs.pop('check', True)
        if check is True:
            for i in doc_or_docs:
                i = self._valid_record(i)
        result = yield self.__collect.insert_many(doc_or_docs, **kwargs)
        raise gen.Return(result)

    @gen.coroutine
    def find_one(self, filter_=None, *args, **kwargs):
        """
        :args
            wrapper wrap result to _record or not

        """
        wrapper = kwargs.pop('wrapper', False)
        result = yield self.__collect.find_one(filter_, *args, **kwargs)
        if wrapper is True:
            raise gen.Return(_record(result))

        raise gen.Return(result)

    @gen.coroutine
    def find_many(self, *args, **kwargs):
        """find many return motor cursor result, limit is required
        coroutine can't return yield genearotr as result,
        instead use a queue do infinite loop
        http://stackoverflow.com/questions/33482066/using-regular-python-generator-in-tornado-coroutine
        """
        wrapper = kwargs.pop('wrapper', False)
        limit = kwargs.get('limit')
        if not limit:
            kwargs['limit'] = 1
        cursor = self.__collect.find(*args, **kwargs)
        result = []
        while (yield cursor.fetch_next):
            doc = cursor.next_object()
            result.append(_record(doc) if wrapper else doc)

        raise gen.Return(result)

    @gen.coroutine
    def update_one(self, filter_, document, **kwargs):
        """update method
        """
        self._valide_update_document(document)
        result = yield self.__collect.update_one(filter_, document, **kwargs)
        raise gen.Return(result)

    @gen.coroutine
    def update_many(self, filter_, document, **kwargs):
        self._valide_update_document(document)
        result = yield self.__collect.update_many(filter_, document, **kwargs)
        raise gen.Return(result)

    @gen.coroutine
    def delete_many(self, filter_):
        if isinstance(filter_, dict) and filter_ == {}:
            raise ValueError("not allowed remove all documents")

        if filter_ is None:
            raise ValueError("not allowed remove all documents")

        result = yield self.__collect.delete_many(filter_)
        raise gen.Return(result)

    @gen.coroutine
    def find_by_id(self, _id, projection=None):
        """find record by _id
        """
        if isinstance(_id, list) or isinstance(_id, tuple):
            result = yield self.find_many(
                {'_id': {'$in': [self._to_primary_key(i) for i in _id]}},
                projection, limit=len(_id))
            raise gen.Return(result)

        document_id = self._to_primary_key(_id)

        if document_id is None:
            raise gen.Return(None)

        result = yield self.__collect.find_one({'_id': document_id}, projection)
        raise gen.Return(result)

    @gen.coroutine
    def remove_by_id(self, _id):
        if isinstance(_id, list) or isinstance(_id, tuple):
            result = yield self.__collect.delete_many(
                {'_id': {'$in': [self._to_primary_key(i) for i in _id]}})
            raise gen.Return(result)

        result = yield self.__collect.delete_one(
            {'_id': self._to_primary_key(_id)})
        raise gen.Return(result)

    @gen.coroutine
    def find_new_one(self, *args, **kwargs):
        cur = self.__collect.find(*args, **kwargs)
        cur.limit(1).sort('_id', DESCENDING)
        for document in (yield cur.to_list(length=1)):
            raise gen.Return(document)

    @gen.coroutine
    def get_as_dict(self, *args, **kwargs):
        """no limit argument, result will be all record in collection
        """
        cur = self.__collect.find(*args, **kwargs)
        as_dict, as_list = {}, []
        while (yield cur.fetch_next):
            doc = cur.next_object()
            as_dict[doc['_id']] = doc
            as_list.append(doc)

        raise gen.Return([as_dict, as_list])

    @gen.coroutine
    def inc(self, filter_, key, num=1):
        result = yield self.__collect.update_one(filter_, {'$inc': {key: num}})
        raise gen.Return(result)


class BaseModel(BaseBaseModel):
    pass
