from django.test import TestCase

from .models import Name

# Create your tests here.

class NameModelTests(TestCase):

    def test_Name_with_not_Japanese(self):
        name1 = Name(lastname_text = 'abc', firstname_text = '翔', sex_text = '男性')
        name2 = Name(lastname_text = '鈴木', firstname_text = '012', sex_text = '女性')
        name3 = Name(lastname_text = '鈴木', firstname_text = '翔', sex_text = '+-=')
        result = name1.setting() and name2.setting() and name3.setting()    
        self.assertIs(result, False)
