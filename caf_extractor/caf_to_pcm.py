# This module extracts the PCM from a CAF file and stores it as an AIFF file.
import os
import collections
import struct


CAFAudioFormat = collections.namedtuple("CAFAudioFormat",
                                        ["sample_rate", "format_id", "format_flags", "bytes_per_packet",
                                         "frames_per_packet", "channels_per_frame", "bits_per_channel"])
wav_header_keys = ["riff", "file_size", "wave", "fmt",
                                         "fmt_data_size", "fmt_type", "nchannels",
                                         "sample_rate", "bytes_per_sample", "bytes_per_channel",
                                         "bits_per_sample", "data_label", "data_size"]
WAVHeader = collections.namedtuple("WAVHeader", wav_header_keys)


wav_header_struct = "4si4s4sihhiihh4si"
wav_header_size = 44


wav_header_dict = {key: None for key in wav_header_keys}
wav_header_dict["riff"] = b'RIFF'
wav_header_dict["wave"] = b'WAVE'
wav_header_dict["fmt"] = b'fmt '
wav_header_dict["fmt_data_size"] = 16
wav_header_dict["fmt_type"] = 1
wav_header_dict["bits_per_sample"] = 16
wav_header_dict["data_label"] = b'data'


def get_wav_header(wav_file):
    """
    Get the header of a WAV file
    :param wav_file:
    :return: returns a WAVHeader that contains the header of the given WAAV file.
    """
    wav_file.seek(0, os.SEEK_SET)
    return WAVHeader._make(struct.unpack(wav_header_struct, wav_file.read(wav_header_size)))


def _copy_caf_data(caf_file, wav_file, wav_header_dict):
    # skip all chunks except the data chunk
    chunk_header_size = 4 + 8
    struct_format = "!4sq"
    header_type, chunk_size = struct.unpack(struct_format, caf_file.read(chunk_header_size))
    while header_type != b'data':
        print(header_type)
        caf_file.seek(chunk_size, os.SEEK_CUR)
        header_type, chunk_size = struct.unpack(struct_format, caf_file.read(chunk_header_size))

    data_size = chunk_size
    if data_size == -1:
        cur_pos = caf_file.tell()
        caf_file.seek(0, os.SEEK_END)
        data_size = caf_file.tell() - cur_pos
    wav_header_dict["data_size"] = data_size
    while data_size > 0:
        data = caf_file.read(128 * 1024)
        nbytes = wav_file.write(data)
        data_size -= nbytes
    wav_header_dict["file_size"] = wav_header_size + wav_header_dict["data_size"]
    wav_header_struct_values = tuple(wav_header_dict[key] for key in wav_header_keys)
    wav_header = struct.pack(wav_header_struct, *wav_header_struct_values)
    wav_file.seek(0, os.SEEK_SET)
    wav_file.write(wav_header)


def write_caf_to_wav(caf_file, wav_file):
    """
    Extract a WAV file from a CAF file that contains a WAV file.
    None of the file objects are closed by this function.
    :param caf_file: The file object for the CAF.
    :param wav_file: The file object for the WAV.
    :return: None
    """
    car_audio_format_start = 20
    # Read audio format
    caf_file.seek(car_audio_format_start)
    caf_audio_format_struct = "!d" + ("I" * 6)
    caf_audio_format = CAFAudioFormat._make(struct.unpack(caf_audio_format_struct,
                                                    caf_file.read(32)))
    wav_header_dict["nchannels"] = int(caf_audio_format.channels_per_frame)
    wav_header_dict["sample_rate"] = int(caf_audio_format.sample_rate)
    wav_header_dict["bytes_per_sample"] = int(wav_header_dict["sample_rate"] * wav_header_dict["bits_per_sample"] * wav_header_dict["nchannels"] // 8)
    wav_header_dict["bytes_per_channel"] = int(wav_header_dict["bits_per_sample"] * wav_header_dict["nchannels"] // 8)
    wav_file.write(b'\x00' * wav_header_size)

    _copy_caf_data(caf_file, wav_file, wav_header_dict)



