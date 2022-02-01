import os
import numpy as np
import pytest
from rec_to_binaries.read_binaries import (
    write_trodes_extracted_datafile,
    readTrodesExtractedDataFile
)

CURRENT_DIRECTORY = os.getcwd()
TEST_PATH = f'{CURRENT_DIRECTORY}/rec_to_binaries/test/e2etests/'

def test_write_trodes_extracted_datafile(e2etests_directory_path, clear_file_content):
    # arrange
    file_path = f'{e2etests_directory_path}/test_data/temp_file.txt'
    data_file = {'a': np.array((1,2,3)), 'data': np.array((4,5,6))}
    clear_file_content(file_path)

    # act
    write_trodes_extracted_datafile(file_path, data_file)

    # assert
    file_lines = []
    with open(file_path, 'r+') as file:
        file_lines = list(file.readlines())

    assert file_lines[0] == '<Start settings>\n'
    assert file_lines[1] == 'a: [1 2 3]\n'
    assert file_lines[2] == '<End settings>\n'
    assert file_lines[3] == '\x04\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00'

def test_readTrodesExtractedDataFile_check_first_line_for_Start_settings(e2etests_directory_path):
    file_path = f'{e2etests_directory_path}/test_data/readTrodesExtractDataFile_not_start_setting.txt'

    with pytest.raises(Exception):
        readTrodesExtractedDataFile(file_path)

def test_readTrodesExtractedDataFile_check_file_is_written_correctly(e2etests_directory_path):
    file_path = f'{e2etests_directory_path}/test_data/readTrodesExtractedDataFile_check_file_is_written_correctly.txt'
    fields_text = readTrodesExtractedDataFile(file_path)

    assert fields_text['a'] == '[1,2,3]'
    assert fields_text['data'].tobytes() == b''

def test_clean_read_binaries_test__suite(e2etests_directory_path, clear_file_content):
    try:
        file_path = f'{e2etests_directory_path}/test_data/temp_file.txt'
        clear_file_content(file_path)
        assert True
    # The exception type is irrelevant. It just needs to be caught
    # pylint: disable=broad-except
    except Exception:
        print('Pytest could not clean up resources')
        assert False
