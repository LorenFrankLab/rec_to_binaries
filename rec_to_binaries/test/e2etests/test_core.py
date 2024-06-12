import pytest
from rec_to_binaries.core import (
    extract_trodes_rec_file,
    convert_binaries_to_hdf5,
)

@pytest.mark.skip(reason='Got to figure out the many cases')
def extract_trodes_rec_file():
    pass

@pytest.mark.skip(reason='Got to figure out - type object \'object\' has no attribute \'dtype')
def test_convert_binaries_to_hdf5_rec_file_write_to_file(e2etests_directory_path):
    data_dir = e2etests_directory_path
    animal = 'test_animal'
    convert_binaries_to_hdf5(data_dir,
                             animal,
                             out_dir=None,
                             dates=None,
                             parallel_instances=1,
                             convert_dio=False,
                             convert_lfp=False,
                             convert_pos=False,
                             convert_spike=False
    )
