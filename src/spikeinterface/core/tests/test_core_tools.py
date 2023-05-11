import platform
from pathlib import Path

import pytest
import numpy as np

from spikeinterface.core import generate_recording
from spikeinterface.core.core_tools import write_binary_recording, write_memory_recording, recursive_path_modifier
from spikeinterface.core.binaryrecordingextractor import BinaryRecordingExtractor
from spikeinterface.core.generate import GeneratorRecording
try:
    from multiprocessing.shared_memory import SharedMemory

    HAVE_SHAREDMEMORY = True
except:
    HAVE_SHAREDMEMORY = False


if hasattr(pytest, "global_test_folder"):
    cache_folder = pytest.global_test_folder / "core"
else:
    cache_folder = Path("cache_folder") / "core"


def test_write_binary_recording(tmp_path):
    # Test write_binary_recording() with loop (n_jobs=1)
    # Setup
    sampling_frequency = 30_000
    num_channels = 2
    dtype = "float32"

    durations = [10.0]
    recording = GeneratorRecording(
        durations=durations, num_channels=num_channels, sampling_frequency=sampling_frequency
    )
    file_paths = [tmp_path / "binary01.raw"]

    # Write binary recording
    job_kwargs = dict(verbose=False, n_jobs=1)
    write_binary_recording(recording, file_paths=file_paths, dtype=dtype, **job_kwargs)

    # Check if written data matches original data
    recorder_binary = BinaryRecordingExtractor(
        file_paths=file_paths, sampling_frequency=sampling_frequency, num_chan=num_channels, dtype=dtype
    )
    assert np.allclose(recorder_binary.get_traces(), recording.get_traces())

def test_write_binary_recording_parallel(tmp_path):
    # Test write_binary_recording() with parallel processing (n_jobs=2)

    # Setup
    sampling_frequency = 30_000
    num_channels = 2
    dtype = "float32"
    durations = [10.30, 3.5]
    recording = GeneratorRecording(
        durations=durations, num_channels=num_channels, sampling_frequency=sampling_frequency, dtype=dtype,
    )
    file_paths = [tmp_path / "binary01.raw", tmp_path / "binary02.raw"]

    # Write binary recording
    job_kwargs = dict(verbose=False, n_jobs=2, chunk_memory="100k")
    write_binary_recording(recording, file_paths=file_paths, dtype=dtype, **job_kwargs)

    # Check if written data matches original data
    recorder_binary = BinaryRecordingExtractor(
        file_paths=file_paths, sampling_frequency=sampling_frequency, num_chan=num_channels, dtype=dtype
    )
    for segment_index in range(recording.get_num_segments()):
        binary_traces = recorder_binary.get_traces(segment_index=segment_index)
        recording_traces = recording.get_traces(segment_index=segment_index)
        assert np.allclose(binary_traces, recording_traces)


def test_write_binary_recording_multiple_segment(tmp_path):
    # Test write_binary_recording() with multiple segments (n_jobs=2)
    # Setup
    sampling_frequency = 30_000
    num_channels = 10
    dtype = "float32"

    durations = [10.30, 3.5]
    recording = GeneratorRecording(
        durations=durations, num_channels=num_channels, sampling_frequency=sampling_frequency
    )
    file_paths = [tmp_path / "binary01.raw", tmp_path / "binary02.raw"]

    # Write binary recording
    job_kwargs = dict(verbose=False, n_jobs=2, chunk_memory="100k")
    write_binary_recording(recording, file_paths=file_paths, dtype=dtype, **job_kwargs)

    # Check if written data matches original data
    recorder_binary = BinaryRecordingExtractor(
        file_paths=file_paths, sampling_frequency=sampling_frequency, num_chan=num_channels, dtype=dtype
    )
    
    for segment_index in range(recording.get_num_segments()):
        binary_traces = recorder_binary.get_traces(segment_index=segment_index)
        recording_traces = recording.get_traces(segment_index=segment_index)
        assert np.allclose(binary_traces, recording_traces)


def test_write_memory_recording():
    # 2 segments
    recording = generate_recording(num_channels=2, durations=[10.325, 3.5])
    # make dumpable
    recording = recording.save()

    # write with loop
    write_memory_recording(recording, dtype=None, verbose=True, n_jobs=1)

    write_memory_recording(recording, dtype=None,
                           verbose=True, n_jobs=1, chunk_memory='100k', progress_bar=True)

    if HAVE_SHAREDMEMORY and platform.system() != 'Windows':
        # write parrallel
        write_memory_recording(recording, dtype=None,
                               verbose=False, n_jobs=2, chunk_memory='100k')

        # write parrallel
        write_memory_recording(recording, dtype=None,
                               verbose=False, n_jobs=2, total_memory='200k', progress_bar=True)



def test_recursive_path_modifier():
    # this test nested depth 2 path modifier
    d = {
        'kwargs':{
            'path' : '/yep/path1',
            'recording': {
                'module': 'mock_module',
                'class': 'mock_class',
                'version': '1.2',
                'annotations': {},
                'kwargs': {
                    'path':'/yep/path2'
                },
            
            }
        }
    }

    d2  =recursive_path_modifier(d, lambda p: p.replace('/yep', '/yop'))
    assert d2['kwargs']['path'].startswith('/yop')
    assert d2['kwargs']['recording']['kwargs'] ['path'].startswith('/yop')


if __name__ == '__main__':
    # Create a temporary folder using the standard library
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_path = Path(tmpdirname)
        test_write_binary_recording_with_chunk_memory(tmp_path)
        #test_write_memory_recording()
        #test_recursive_path_modifier()
