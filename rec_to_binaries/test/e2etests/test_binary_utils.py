import pytest
from rec_to_binaries.binary_utils import (
    TrodesBinaryFormatError,
    TrodesBinaryReader,
    TrodesLFPBinaryLoader,
    TrodesTimestampBinaryLoader,
    TrodesSpikeBinaryLoader,
    TrodesPosBinaryLoader,
    TrodesDIOBinaryLoader,
)

def test_TrodesBinaryReader_first_line_not_Start_settings_error(e2etests_directory_path):
    file_path = f'{e2etests_directory_path}/test_data/TrodesBinaryReader_test_first_line_exception.txt'

    with pytest.raises(TrodesBinaryFormatError) as ex:
        trodes_binary_reader = TrodesBinaryReader(file_path)


def test_TrodesBinaryReader_more_than_1000_length_error(e2etests_directory_path):
    file_path = f'{e2etests_directory_path}/test_data/TrodesBinaryReader_test_more_than_1000_line_exception.txt'

    with pytest.raises(TrodesBinaryFormatError):
        trodes_binary_reader = TrodesBinaryReader(file_path)
 
def test_TrodesBinaryReader_check_if_valid_file_is_read(e2etests_directory_path):
    file_path = f'{e2etests_directory_path}/test_data/TrodesBinaryReader_check_if_valid_file_is_read.txt'
    trodes_binary_reader = TrodesBinaryReader(file_path)
    
    assert trodes_binary_reader.data_start_byte == 43
    assert trodes_binary_reader.header_params == {'a': '1', 'data': '2'}

def test_TrodesLFPBinaryLoader_check_if_file_can_be_read(e2etests_directory_path):
    file_path = f'{e2etests_directory_path}/test_data/TrodesLFPBinaryLoader_test_file_read.txt'
    trodes_LFP_binary_loader = TrodesLFPBinaryLoader(file_path)
    
    assert trodes_LFP_binary_loader.header_params['Original_file'] == 'test_Original_file'
    assert trodes_LFP_binary_loader.header_params['Trode_ID'] == 'test_Trode_ID'
    assert trodes_LFP_binary_loader.header_params['Trode_channel'] == 'test_Trode_channel'
    assert trodes_LFP_binary_loader.header_params['Clock rate'] == 'test_Clock rate'
    assert trodes_LFP_binary_loader.header_params['Voltage_scaling'] == 'test_Voltage_scaling'
    assert trodes_LFP_binary_loader.header_params['Decimation'] == 'test_Decimation'
    assert trodes_LFP_binary_loader.header_params['First_timestamp'] == 'test_First_timestamp'
    assert trodes_LFP_binary_loader.header_params['Reference'] == 'test_Reference'
    assert trodes_LFP_binary_loader.header_params['Low_pass_filter'] == 'test_Low_pass_filter'
    assert trodes_LFP_binary_loader.header_params['Fields'] == 'test_Fields'

def test_TrodesTimestampBinaryLoader_check_if_file_can_be_read(e2etests_directory_path):
    file_path = f'{e2etests_directory_path}/test_data/TrodesTimestampBinaryLoader_test_file_read.txt'
    trodes_timestamp_binary_loader = TrodesTimestampBinaryLoader(file_path)

    assert trodes_timestamp_binary_loader.header_params['Byte_order'] == 'test_Byte_order'
    assert trodes_timestamp_binary_loader.header_params['Original_file'] == 'test_Original_file'
    assert trodes_timestamp_binary_loader.header_params['Clock rate'] == 'test_Clock rate'
    assert trodes_timestamp_binary_loader.header_params['Decimation'] == 'test_Decimation'
    assert trodes_timestamp_binary_loader.header_params['Time_offset'] == 'test_Time_offset'
    assert trodes_timestamp_binary_loader.header_params['Fields'] == 'test_Fields'

def test_TrodesSpikeBinaryLoader_check_if_data_file_is_read(e2etests_directory_path):
    file_path = f'{e2etests_directory_path}/test_data/TrodesSpikeBinaryLoader_test_file_read.txt'
    trodes_spike_binary_loader = TrodesSpikeBinaryLoader(file_path)

    
    assert trodes_spike_binary_loader.header_params['Original_file'] == 'test_Original_file'
    assert trodes_spike_binary_loader.header_params['nTrode_ID'] == '1'
    assert trodes_spike_binary_loader.num_channels == 10
    assert trodes_spike_binary_loader.header_params['Clock rate'] == '3'
    assert trodes_spike_binary_loader.header_params['Voltage_scaling'] == 'v'
    assert trodes_spike_binary_loader.header_params['Time_offset'] == '4'
    assert trodes_spike_binary_loader.header_params['Threshold'] == '5'
    assert trodes_spike_binary_loader.header_params['Spike_invert'] == 't'
    assert trodes_spike_binary_loader.header_params['Reference'] == '6'
    assert trodes_spike_binary_loader.header_params['ReferenceNTrode'] == '7'
    assert trodes_spike_binary_loader.header_params['ReferenceChannel'] == '8'
    assert trodes_spike_binary_loader.header_params['Filter'] == 't'
    assert trodes_spike_binary_loader.header_params['lowPassFilter'] == 'y'
    assert trodes_spike_binary_loader.header_params['highPassFilter'] == 'n'
    assert trodes_spike_binary_loader.header_params['Fields'] == 'test_field'
    assert trodes_spike_binary_loader.spike_rec_size == 804

@pytest.mark.skip(reason="I have to figure out why pos_list stays empty")
def test_TrodesPosBinaryLoader_check_if_data_file_is_read(e2etests_directory_path):
    file_path = f'{e2etests_directory_path}/test_data/TrodesPosBinaryLoader_check_if_data_file_is_read.txt'
    trodes_pos_binary_loader = TrodesPosBinaryLoader(file_path)

    breakpoint()
    
    assert trodes_pos_binary_loader.header_params['threshold'] == 'test_threshold'
    assert trodes_pos_binary_loader.header_params['dark'] == 'test_dark'
    assert trodes_pos_binary_loader.header_params['clockrate'] == 'test_clockrate'
    assert trodes_pos_binary_loader.header_params['field_str'] == 'test_Fields'
    assert trodes_pos_binary_loader.rec_size == 12
    assert trodes_pos_binary_loader.unpack_format == 'IHHHH'

@pytest.mark.skip(reason="I have to figure out why pos_list stays empty")
def test_TrodesDIOBinaryLoader_check_if_data_file_is_read(e2etests_directory_path):
    file_path = f'{e2etests_directory_path}/test_data/TrodesPosBinaryLoader_check_if_data_file_is_read.txt'
    trodes_pos_binary_loader = TrodesDIOBinaryLoader(file_path)
    
    assert True
