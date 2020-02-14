import unittest
from app import app
import pymongo
import flask
import pandas as pd
from pymongo import MongoClient
import json

file_name="Edu.csv"
data = pd.read_csv('FlaskWithMongoDB-master/data/'+file_name)
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
        pass
    
    def tearDown(self):
        pass
    #Check the values of Gender variable
    def test_valid_gender_values(self):
        cursor=stu_col.find({})
        stu_col1=stu_col.find({})
        for i in stu_col1:
            self.assertIn(i['Gender'],'M|F')
            
    #Check the functioning of Home Page
    def test_home_page(self):
        response=self.app.get('/index')
        self.assertEqual(response.status_code,200)
        
    #Check the functioning of "All Students" page
    def test_view(self):
        response=self.app.get('/list')
        self.assertEqual(response.status_code,200)        
       
    #Check the values of Predicted Class variable
     def test_valid_predicted_class_values(self):
        cursor=stu_col.find({})
        stu_col1=stu_col.find({})
        for i in stu_col1:
            self.assertIn(i['Class'],'L|M|H')
    

















if __name__ == '__main__':
    unittest.main()
