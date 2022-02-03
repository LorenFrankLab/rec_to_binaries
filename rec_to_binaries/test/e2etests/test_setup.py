import os
import pkg_resources


def test_check_spikegadget_is_installed():
    home_directory = os.path.expanduser('~')
    spike_gadget_path = f'{home_directory}/SpikeGadgets'
    spike_gadget_exists = os.path.isdir(spike_gadget_path)
    assert spike_gadget_exists

def test_check_if_rec_to_binaries_is_installed():
    package = pkg_resources.get_distribution('rec_to_binaries')

    assert package is not None

def test_major_mountainlab_pytools_version_number_is_useable():
    package = pkg_resources.get_distribution('mountainlab-pytools')

    assert package is not None
    assert package.version.split('.')[0] == '0', 'Major semver update, smoke test code'
    assert package.version.split('.')[1] >= '7', 'Minor semver downgrade, check installation'
