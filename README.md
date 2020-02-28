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

### Installation
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


### Usage
```python
import logging
from rec_to_binaries import extract_trodes_rec_file

logging.basicConfig(level='INFO', format='%(asctime)s %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

data_dir = 'test_data/'
animal = 'lotus'

extract_trodes_rec_file(data_dir, animal, parallel_instances=4)

```
### Common Issues
+ Problem: `rec_to_binaries` is not finding my files.
  Solution: Data is not in the correct file structure. See below for the expected format.
+ Problem: `rec_to_binaries` can't find a function.
  Solution: Make sure you have Trodes installed and on your path.
+ Problem: `rec_to_binaries` won't import.
  Solution: If you used conda then make sure the environment you installed `rec_to_binaries` in is activated.

### Example file structure (in folder `test_data/`)

#### Before running `extract_trodes_rec_file`
```bash
.
|-- lotus
|   |
|   `-- raw
|       `-- 20190902
|           |-- 20190902_lotus_06_r3.1.h264
|           |-- 20190902_lotus_06_r3.1.trackgeometry
|           |-- 20190902_lotus_06_r3.1.videoPositionTracking
|           |-- 20190902_lotus_06_r3.1.videoTimeStamps
|           |-- 20190902_lotus_06_r3.1.videoTimeStamps.cameraHWSync
|           |-- 20190902_lotus_06_r3.rec
|           `-- 20190902_lotus_06_r3.stateScriptLog
`-- README.md

```
#### After running `extract_trodes_rec_file`
```bash
.
|-- lotus
|   |-- preprocessing
|   |   `-- 20190902
|   |       |-- 20190902_lotus_06_r3.1.pos
|   |       |   |-- 20190902_lotus_06_r3.1.pos_cameraHWFrameCount.dat
|   |       |   |-- 20190902_lotus_06_r3.1.pos_online.dat
|   |       |   `-- 20190902_lotus_06_r3.1.pos_timestamps.dat
|   |       |-- 20190902_lotus_06_r3.analog
|   |       |   |-- 20190902_lotus_06_r3.analog_AccelX.dat
|   |       |   |-- 20190902_lotus_06_r3.analog_AccelY.dat
|   |       |   |-- 20190902_lotus_06_r3.analog_AccelZ.dat
|   |       |   |-- 20190902_lotus_06_r3.analog_GyroX.dat
|   |       |   |-- 20190902_lotus_06_r3.analog_GyroY.dat
|   |       |   |-- 20190902_lotus_06_r3.analog_GyroZ.dat
|   |       |   |-- 20190902_lotus_06_r3.analog_MagX.dat
|   |       |   |-- 20190902_lotus_06_r3.analog_MagY.dat
|   |       |   |-- 20190902_lotus_06_r3.analog_MagZ.dat
|   |       |   |-- 20190902_lotus_06_r3.exportanalog.log
|   |       |   `-- 20190902_lotus_06_r3.timestamps.dat
|   |       |-- 20190902_lotus_06_r3.DIO
|   |       |   |-- 20190902_lotus_06_r3.dio_Din10.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din11.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din12.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din13.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din14.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din15.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din16.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din17.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din18.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din19.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din1.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din20.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din21.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din22.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din23.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din24.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din25.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din26.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din27.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din28.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din29.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din2.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din30.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din31.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din32.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din3.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din4.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din5.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din6.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din7.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din8.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Din9.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout10.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout11.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout12.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout13.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout14.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout15.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout16.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout17.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout18.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout19.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout1.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout20.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout21.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout22.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout23.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout24.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout25.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout26.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout27.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout28.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout29.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout2.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout30.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout31.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout32.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout3.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout4.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout5.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout6.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout7.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout8.dat
|   |       |   |-- 20190902_lotus_06_r3.dio_Dout9.dat
|   |       |   `-- 20190902_lotus_06_r3.exportdio.log
|   |       |-- 20190902_lotus_06_r3.LFP
|   |       |   |-- 20190902_lotus_06_r3.exportLFP.log
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt10ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt11ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt12ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt13ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt14ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt15ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt16ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt17ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt18ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt19ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt1ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt20ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt21ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt22ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt23ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt24ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt25ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt26ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt27ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt28ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt29ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt2ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt30ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt31ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt32ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt3ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt4ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt5ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt6ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt7ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt8ch1.dat
|   |       |   |-- 20190902_lotus_06_r3.LFP_nt9ch1.dat
|   |       |   `-- 20190902_lotus_06_r3.timestamps.dat
|   |       |-- 20190902_lotus_06_r3.mda
|   |       |   |-- 20190902_lotus_06_r3.exportmda.log
|   |       |   |-- 20190902_lotus_06_r3.nt10.mda
|   |       |   |-- 20190902_lotus_06_r3.nt11.mda
|   |       |   |-- 20190902_lotus_06_r3.nt12.mda
|   |       |   |-- 20190902_lotus_06_r3.nt13.mda
|   |       |   |-- 20190902_lotus_06_r3.nt14.mda
|   |       |   |-- 20190902_lotus_06_r3.nt15.mda
|   |       |   |-- 20190902_lotus_06_r3.nt16.mda
|   |       |   |-- 20190902_lotus_06_r3.nt17.mda
|   |       |   |-- 20190902_lotus_06_r3.nt18.mda
|   |       |   |-- 20190902_lotus_06_r3.nt19.mda
|   |       |   |-- 20190902_lotus_06_r3.nt1.mda
|   |       |   |-- 20190902_lotus_06_r3.nt20.mda
|   |       |   |-- 20190902_lotus_06_r3.nt21.mda
|   |       |   |-- 20190902_lotus_06_r3.nt22.mda
|   |       |   |-- 20190902_lotus_06_r3.nt23.mda
|   |       |   |-- 20190902_lotus_06_r3.nt24.mda
|   |       |   |-- 20190902_lotus_06_r3.nt25.mda
|   |       |   |-- 20190902_lotus_06_r3.nt26.mda
|   |       |   |-- 20190902_lotus_06_r3.nt27.mda
|   |       |   |-- 20190902_lotus_06_r3.nt28.mda
|   |       |   |-- 20190902_lotus_06_r3.nt29.mda
|   |       |   |-- 20190902_lotus_06_r3.nt2.mda
|   |       |   |-- 20190902_lotus_06_r3.nt30.mda
|   |       |   |-- 20190902_lotus_06_r3.nt31.mda
|   |       |   |-- 20190902_lotus_06_r3.nt32.mda
|   |       |   |-- 20190902_lotus_06_r3.nt3.mda
|   |       |   |-- 20190902_lotus_06_r3.nt4.mda
|   |       |   |-- 20190902_lotus_06_r3.nt5.mda
|   |       |   |-- 20190902_lotus_06_r3.nt6.mda
|   |       |   |-- 20190902_lotus_06_r3.nt7.mda
|   |       |   |-- 20190902_lotus_06_r3.nt8.mda
|   |       |   |-- 20190902_lotus_06_r3.nt9.mda
|   |       |   `-- 20190902_lotus_06_r3.timestamps.mda
|   |       |-- 20190902_lotus_06_r3.mountain
|   |       |-- 20190902_lotus_06_r3.spikes
|   |       |   |-- 20190902_lotus_06_r3.exportspikes.log
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt10.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt11.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt12.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt13.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt14.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt15.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt16.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt17.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt18.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt19.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt1.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt20.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt21.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt22.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt23.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt24.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt25.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt26.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt27.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt28.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt29.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt2.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt30.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt31.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt32.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt3.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt4.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt5.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt6.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt7.dat
|   |       |   |-- 20190902_lotus_06_r3.spikes_nt8.dat
|   |       |   `-- 20190902_lotus_06_r3.spikes_nt9.dat
|   |       `-- 20190902_lotus_06_r3.time
|   |           |-- 20190902_lotus_06_r3.continuoustime.dat
|   |           |-- 20190902_lotus_06_r3.exporttime.log
|   |           `-- 20190902_lotus_06_r3.time.dat
|   `-- raw
|       `-- 20190902
|           |-- 20190902_lotus_06_r3.1.h264
|           |-- 20190902_lotus_06_r3.1.trackgeometry
|           |-- 20190902_lotus_06_r3.1.videoPositionTracking
|           |-- 20190902_lotus_06_r3.1.videoTimeStamps
|           |-- 20190902_lotus_06_r3.1.videoTimeStamps.cameraHWSync
|           |-- 20190902_lotus_06_r3.rec
|           `-- 20190902_lotus_06_r3.stateScriptLog
`-- README.md

```
