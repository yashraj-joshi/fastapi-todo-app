import pytest

# def test_equal_or_not_equal():
#     assert 1 == 1
#     assert 2 == 2
#
# def test_is_instance():
#     assert isinstance("this is a string",str)
#     assert not isinstance('10',int)
#
# def test_boolean():
#     validated = True
#     assert validated is True
#     assert ('hello' == 'world') is False
#
# def test_type():
#     assert type('hello') is str

class Student:
    def __init__(self,firstname:str,lastname:str,major:str,years:int):
        self.firstname = firstname
        self.lastname = lastname
        self.major = major
        self.years = years

@pytest.fixture
def default_employee():
    return Student('John','Doe','Computer Science',3)

def test_person_initialization(default_employee):
    assert default_employee.firstname == 'John','Firstname is should be John'
    assert default_employee.lastname == 'Doe','Lastname is should be Doe'
    assert default_employee.major == 'Computer Science'
    assert default_employee.years == 3

# print("Test is running")
# def test_something(default_employee):
#     assert default_employee.firstname == "Yash","Test failed"