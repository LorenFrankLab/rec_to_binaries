from unittest.mock import MagicMock, patch
import pytest
from faker import Faker
from rec_to_binaries.adjust_timestamps import (
    _label_time_chunks,
    fix_timestamp_lag
)


@patch('numpy.asarray')
@patch('numpy.diff')
@patch('numpy.insert')
@patch('numpy.cumsum')
def test___label_time_chunks(mock_cumsum, mock_insert, mock_diff, mock_asarray):
    test_argument = 5
    test_diff_val = 10
    test_insert_val = 20
    mock_diff.return_value = test_diff_val
    mock_insert.return_value = test_insert_val

    _label_time_chunks(test_argument)

    assert mock_asarray.called
    assert mock_diff.called
    assert mock_insert.called
    assert mock_asarray.call_args[0][0] == test_argument
    assert mock_cumsum.called
    assert mock_cumsum.call_args[0][0] == test_insert_val


@pytest.mark.parametrize('names', ['', 'systime'])
@patch('rec_to_binaries.adjust_timestamps._insert_new_data')
@patch('rec_to_binaries.adjust_timestamps.readTrodesExtractedDataFile')
@patch('rec_to_binaries.adjust_timestamps.logger')
@patch('rec_to_binaries.adjust_timestamps.write_trodes_extracted_datafile')
@patch('pandas.DataFrame')
@patch('rec_to_binaries.adjust_timestamps.infer_systime')
def test_fix_timestamp_lag(
        mock_infer_systime,
        mock_pandas_DataFrame,
        mock_write_trodes_extracted_datafile,
        mock_logger,
        mock_readTrodesExtractedDataFile,
        mock__insert_new_data,
        names
    ):  
    #fix_timestamp_lag
    fake = Faker()
    mock_logger.return_value.warn.return_value = fake.numerify()
    mock__insert_new_data.return_value = fake.numerify()
    mock_write_trodes_extracted_datafile.return_value = fake.word()
    fake_continuoustime_filename = fake.file_name()
    magicMock = MagicMock()
    fake_data_file = MagicMock()
    fake_data_file_return = MagicMock()
    fake_data_file_return.names = names
    fake_data_file.return_value = { 'data': fake_data_file }
       
    mock_readTrodesExtractedDataFile.return_value = fake_data_file
    mock_infer_systime.return_value = fake.word()
    
    fix_timestamp_lag(fake_continuoustime_filename)
    
    assert mock_readTrodesExtractedDataFile.called
    assert 'systime' in names or not mock_logger.called
    assert not 'systime' in names or not mock_pandas_DataFrame.called
    assert mock__insert_new_data.called
    assert mock_write_trodes_extracted_datafile.called
