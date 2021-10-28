# This module extracts the PCM from a CAF file and stores it as an AIFF file.
import os
import wave


class CafElement:
    def __init__(self, start, size=32):
        self.start = start
        self.size = size

    @property
    def next_start(self):
        return self.start + self.size


caf_header = CafElement(start=0, size=32+16*2)
caf_audio_desc = CafElement(start=caf_header.next_start)
caf_sample_rate = CafElement(start=caf_audio_desc.next_start, size=64)
caf_format_id = CafElement(start=caf_sample_rate.next_start)
caf_format_flags = CafElement(start=caf_format_id.next_start)
caf_bytes_per_packet = CafElement(start=caf_format_flags.next_start)
caf_frames_per_packet = CafElement(start=caf_bytes_per_packet.next_start)
caf_channels_per_frame = CafElement(start=caf_frames_per_packet.next_start)
caf_bits_per_channel = CafElement(start=caf_channels_per_frame.next_start)

chunk_header_type_size = 32
chunk_header_size_size = 64


def copy_caf_data(caf_file, wav_file, frame_size, start):
    # skip all chunks except the data chunk
    caf_file.seek(start)
    header_type = caf_file.read(chunk_header_type_size)
    while header_type != b'data':
        header_size = int(caf_file.read(chunk_header_size_size))
        caf_file.seek(header_size + caf_file.tell())
        header_type = caf_file.read(chunk_header_type_size)
    data_size = caf_file.read(chunk_header_size_size)
    if data_size == -1:
        cur_pos = caf_file.tell()
        caf_file.seek(0, os.SEEK_END)
        data_size = caf_file.tell() - cur_pos
    nframes = 0
    while data_size > 0:
        wav_file.writeframesraw(caf_file.read(frame_size))
        data_size -= frame_size
        nframes += 1
    wav_file.setnframes(nframes)
    wav_file.close()







aiff_chunk_id = b'FORM'
aiff_common_chunk_id = b'COMM'
aiff_sound_data_chunk = b'SSND'
aiff_form_type = b'AIFF'

# ckSize is the size of the data portion of the chunk, in bytes. It does not include the 8 bytes used
# by ckID and ckSize.
aiff_chunk_size = b'fedcba9876543210'

# ckData contains the data stored in the chunk. The format of this data is determined by ckID. If
# the data is an odd number of bytes in length, a zero pad byte must be added at the end. The pad
# byte is not included in ckSize .
aiff_chunks = []
