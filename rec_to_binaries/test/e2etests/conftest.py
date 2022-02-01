import pytest
import os

CURRENT_DIRECTORY = os.getcwd()

def _clear_file_content(file_path):
    if file_path is None or file_path.strip() == '':
        raise FileNotFoundError
    with open(file_path, 'r+') as file:
        file.truncate(0)

@pytest.fixture
def e2etests_directory_path():
    return f'{CURRENT_DIRECTORY}/rec_to_binaries/test/e2etests/'

@pytest.fixture
def current_directory():
    return CURRENT_DIRECTORY

@pytest.fixture
def clear_file_content():
    return _clear_file_content
