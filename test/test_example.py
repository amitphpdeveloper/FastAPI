import pytest

def test_is_equal_or_not():
    assert 3 == 3
    assert 3 != 1

def test_is_value_string():
    assert isinstance("Hello world", str)
    assert isinstance(10, int)


def test_type_boolean():
    validate = True
    assert validate is True
    assert (3 == 5) is False


def test_type_var():
    assert type("Hello" is str)
    assert type(4 is int)
    assert type(True is bool)
    assert type([1,2,3,4] is list)
    assert type({1,2,3} is dict)
    assert type(("test","apple") is tuple)
    assert type((1,2,3) is set)


def test_arithmetic_condition():
    assert 10 > 3
    assert 5 ** 2 == 25

def test_list():
    num_list = [1,2,3,4]
    any_list = [False, False]
    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)
    assert all(any_list) == False
    assert not any(any_list)

class Employee:
    def __init__(self, first_name: str, last_name: str,salary: int, total_experience: int):
        self.first_name = first_name
        self.last_name = last_name
        self.salary = salary
        self.total_experience = total_experience


@pytest.fixture()
def employee_fixture():
    return Employee("Amit", "Solanki", 400000, 10)

def test_employee_object(employee_fixture):
    assert employee_fixture.first_name == 'Amit', "First name should be Amit"
    assert employee_fixture.last_name == 'Solanki', "First name should be Solanki"
    assert employee_fixture.salary == 400000, "Salary should be 400000"
    assert employee_fixture.total_experience == 10

