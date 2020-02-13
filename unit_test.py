import unittest
from app import app
import os
import pymongo
import flask
from flask import url_for
import pandas as pd
from pymongo import MongoClient
from mockupdb import MockupDB, go, Command
from bson import ObjectId as mockup_oid
file_name="Edu_test.csv"
import json
from mockupdb import MockupDB, go, Command
data = pd.read_csv('data/'+file_name)
client = MongoClient("mongodb://127.0.0.1:27017") #host uri
db = client.mymongodb    #Select the database
stu_col = db.student #Select the collection name
data_json = json.loads(data.to_json(orient='records'))
stu_col.remove()
stu_col.insert(data_json)

from os import environ
class TestObjectCreation(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        app.config['MONGO_URI'] = environ.get('MONGO_URI')
        self.app = app.test_client()
        self.server = MockupDB(auto_ismaster=True, verbose=True)
        self.server.run()
        # app.testing = True
        # app.config['MONGO_URI'] = self.server.uri
        # self.app = app.test_client()
        pass
    
    def tearDown(self):
        pass
    
    def test_valid_gender_values(self):
        cursor=stu_col.find({})
        stu_col1=stu_col.find({})
        for i in stu_col1:
            self.assertIn(i['Gender'],'M|F')
            
    def test_home_page(self):
        response=self.app.get('/index')
        self.assertEqual(response.status_code,200)
        
    def test_view(self):
        response=self.app.get('/list')
        self.assertEqual(response.status_code,200)        
        
    # def test_valid_delete(self):
        # id = '5a8f1e368f7936badfbb0cfa'
        # future = go(self.app.delete, '/remove/')
        # request = self.server.receives(Command({'delete': 'stu_col', 'ordered': True, 'deletes': [{'q': {'_id': mockup_oid(id)}, 'limit': 1}]}, namespace='app'))
        # request.ok({'acknowledged': True, 'n': 1})
        # http_response = future()
        # self.assertEqual(http_response.status_code, 404)
    

















if __name__ == '__main__':
    unittest.main()