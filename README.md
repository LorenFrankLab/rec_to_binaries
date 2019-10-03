# rec_to_binaries
`rec_to_binaries` is a python package that converts SpikeGadgets rec files in the Frank lab directory format to more useable binaries with the same directory format. The binaries are more useable because the data in the rec files has been broken out into separate categories.

The package wraps C++ functions provided by SpikeGadgets in order to put everything into the correct directory structure. It extracts rec files in the `/raw` folder to binaries to the `/preprocessing` folder.

The binaries are separated out into:
+ analog
+ DIO
+ LFP
+ mda (for mountainSort spike sorting)
+ spikes (for trodes spike sorting)
+ time

# Installation
1. Download SpikeGadgets and install (https://bitbucket.org/mkarlsso/trodes/downloads/)
2. Add SpikeGadgets to path (assuming the SpikeGadgets is in the default location)
```bash
export PATH="$HOME/SpikeGadgets/:$PATH"
```
3. Download and install miniconda (https://docs.conda.io/en/latest/miniconda.html) if conda isn't installed.
4. Install `rec_to_binaries` package into a conda environment
```bash
conda install -c franklab rec_to_binaries
```
5. Convert rec to binaries
```python
import logging
from rec_to_binaries import extract_trodes_rec_file

logging.basicConfig(level='INFO', format='%(asctime)s %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

data_dir = 'test_data/'
animal = 'lotus'

extract_trodes_rec_file(data_dir, animal, parallel_instances=4)

```
