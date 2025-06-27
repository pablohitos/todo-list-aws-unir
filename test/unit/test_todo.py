import warnings
import unittest
import boto3
from moto import mock_dynamodb
import os
import json

@mock_dynamodb
class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        print('---------------------')
        print('Start: setUp')

        # Forzar la variable de entorno que espera el código
        os.environ['DYNAMODB_TABLE'] = 'todoListTable'

        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.is_local = 'true'
        self.uuid = "123e4567-e89b-12d3-a456-426614174000"
        self.text = "Aprender DevOps y Cloud en la UNIR"

        from src.todoList import create_todo_table
        self.table = create_todo_table(self.dynamodb)
        print('End: setUp')

    def tearDown(self):
        print('---------------------')
        print('Start: tearDown')
        self.table.delete()
        print('Table deleted successfully')
        self.dynamodb = None
        print('End: tearDown')

    def test_table_exists(self):
        print('---------------------')
        print('Start: test_table_exists')
        print('Table name:' + self.table.name)
        tableName = os.environ['DYNAMODB_TABLE']
        self.assertIn(tableName, self.table.name)
        print('End: test_table_exists')

    def test_put_todo(self):
        print('---------------------')
        print('Start: test_put_todo')
        from src.todoList import put_item
        response = put_item(self.text, self.dynamodb)
        print('Response put_item:' + str(response))
        self.assertEqual(200, response['statusCode'])
        print('End: test_put_todo')

    def test_put_todo_error(self):
        print('---------------------')
        print('Start: test_put_todo_error')
        from src.todoList import put_item
        self.assertRaises(Exception, put_item, "", self.dynamodb)
        print('End: test_put_todo_error')

    def test_get_todo(self):
        print('---------------------')
        print('Start: test_get_todo')
        from src.todoList import get_item, put_item
        responsePut = put_item(self.text, self.dynamodb)
        print('Response put_item:' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        print('Id item:' + idItem)
        self.assertEqual(200, responsePut['statusCode'])
        responseGet = get_item(idItem, self.dynamodb)
        print('Response Get:' + str(responseGet))
        self.assertEqual(self.text, responseGet['text'])
        print('End: test_get_todo')

    def test_list_todo(self):
        print('---------------------')
        print('Start: test_list_todo')
        from src.todoList import put_item, get_items
        put_item(self.text, self.dynamodb)
        result = get_items(self.dynamodb)
        print('Response GetItems' + str(result))
        self.assertTrue(len(result) == 1)
        self.assertTrue(result[0]['text'] == self.text)
        print('End: test_list_todo')

    def test_update_todo(self):
        print('---------------------')
        print('Start: test_update_todo')
        from src.todoList import put_item, update_item
        updated_text = "Aprender más cosas que DevOps y Cloud en la UNIR"
        responsePut = put_item(self.text, self.dynamodb)
        print('Response PutItem' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        print('Id item:' + idItem)
        result = update_item(idItem, updated_text, "false", self.dynamodb)
        print('Result Update Item:' + str(result))
        self.assertEqual(result['text'], updated_text)
        print('End: test_update_todo')

    def test_update_todo_error(self):
        print('---------------------')
        print('Start: test_update_todo_error')
        from src.todoList import put_item, update_item
        updated_text = "Aprender más cosas que DevOps y Cloud en la UNIR"
        responsePut = put_item(self.text, self.dynamodb)
        print('Response PutItem:' + str(responsePut))
        self.assertRaises(Exception, update_item, updated_text, "", "false", self.dynamodb)
        self.assertRaises(TypeError, update_item, "", self.uuid, "false", self.dynamodb)
        self.assertRaises(Exception, update_item, updated_text, self.uuid, "", self.dynamodb)
        print('End: test_update_todo_error')

    def test_delete_todo(self):
        print('---------------------')
        print('Start: test_delete_todo')
        from src.todoList import delete_item, put_item, get_items
        responsePut = put_item(self.text, self.dynamodb)
        print('Response PutItem:' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        print('Id item:' + idItem)
        delete_item(idItem, self.dynamodb)
        print('Item deleted successfully')
        self.assertTrue(len(get_items(self.dynamodb)) == 0)
        print('End: test_delete_todo')

    def test_delete_todo_error(self):
        print('---------------------')
        print('Start: test_delete_todo_error')
        from src.todoList import delete_item
        self.assertRaises(TypeError, delete_item, "", self.dynamodb)
        print('End: test_delete_todo_error')


if __name__ == '__main__':
    unittest.main()
