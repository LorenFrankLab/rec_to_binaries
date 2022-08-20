import pytest
import numpy as np
from rec_to_binaries.adjust_timestamps import (
    fix_timestamp_lag,
)

@pytest.mark.skip(reason='not implemented')
def test_fix_timestamp_lag_check_if_data_is_written_no_systime(e2etests_directory_path, clear_file_content):
#     # arrange
#     file_path = f'{e2etests_directory_path}/test_data/fix_timestamp_lag_check_if_data_is_written_no_systime.txt'
#     clear_file_content(file_path)
#     fake_data = np.array([
#         ('just', 1),
#         ('another', 2),
#         ('part', 3)], dtype=[('one', 'b1'), ('two', '<b1')]
#     )
#     with open(file_path, "wb") as file:
#         file.write(bytes(b'<Start settings>'))
#         file.write(bytes(b'\n'))
#         file.write(b'data: ')
#         file.write(fake_data)
#         file.write(bytes(b'\n'))
#         file.write(bytes(b'<End settings>'))

#     fix_timestamp_lag(file_path)
#     # act

#     # assert
    pass
