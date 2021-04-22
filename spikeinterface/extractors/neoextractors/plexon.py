import neo

from .neobaseextractor import NeoBaseRecordingExtractor, NeoBaseSortingExtractor


class PlexonRecordingExtractor(NeoBaseRecordingExtractor):
    """
    Class for reading plexon plx files.
    
    Based on neo.rawio.PlexonRawIO
    
    Parameters
    ----------
    file_path: str
        The xml  file.
    stream_id: str or None
    """ 
    mode = 'file'
    NeoRawIOClass = 'PlexonRawIO'

    def __init__(self, file_path, stream_id=None):
        neo_kwargs = {'filename' : file_path}
        NeoBaseRecordingExtractor.__init__(self, stream_id=stream_id, **neo_kwargs)