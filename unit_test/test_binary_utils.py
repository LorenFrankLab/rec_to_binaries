from rec_to_binaries.binary_utils import (
    TrodesBinaryReader,
)
from unittest.mock import MagicMock, patch, mock_open
import pytest
from faker import Faker


# @pytest.mark.parametrize('fake_read_line', [b'<Start settings>\n'])
# @patch('rec_to_binaries.binary_utils.TrodesBinaryReader')
# def test_TrodesBinaryReader__init__(mock_TrodesBinaryReader, fake_read_line):
#     faker = Faker()
#     fake_file_path = faker.file_path()
#     m = mock_open()
#     breakpoint();
#     mock_TrodesBinaryReader.file.readline.return_value = faker.numerify()
#     mock_TrodesBinaryReader.file = []
#     with patch('__main__.open', m, create=True):
#         with open(faker.word(), 'w') as h:
#             h.readline(faker.numerify())
  
#     trodesBinaryReader = TrodesBinaryReader(fake_file_path)
    
    
#     assert False



# >>> with patch('__main__.open', m, create=True):
# ...     with open('foo', 'w') as h:
# ...         h.write('some stuff')

# class TrodesBinaryReader:
#     def __init__(self, path):
#         self.path = path
#         with open(path, 'rb') as file:
#             # reading header
#             # read first line to make sure its a trodes binary header
#             line = file.readline()
#             if line != b'<Start settings>\n':
#                 raise TrodesBinaryFormatError(
#                     'File ({}) does not start with Trodes header <Start settings>'
#                     .format(path))
#             # read header not including start and end tags
#             self.header_params = {}
#             for line_no, line in enumerate(file):
#                 if line == b'<End settings>\n':
#                     break
#                 if line_no > 1000:
#                     raise TrodesBinaryFormatError('File ({}) header over 1000 lines without <End settings>'
#                                                   .format(path))
#                 line_split = line.decode('utf-8').split(':', 1)
#                 self.header_params[line_split[0]] = line_split[1].strip()

#             self.data_start_byte = file.tell()

# >>> m = mock_open()
# >>> with patch('__main__.open', m, create=True):
# ...     with open('foo', 'w') as h:
# ...         h.write('some stuff')

# >>> m.mock_calls
# [call('foo', 'w'),
#  call().__enter__(),
#  call().write('some stuff'),
#  call().__exit__(None, None, None)]
# >>> m.assert_called_once_with('foo', 'w')
# >>> handle = m()
# >>> handle.write.assert_called_once_with('some stuff')

