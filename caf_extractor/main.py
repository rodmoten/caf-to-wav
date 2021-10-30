import argparse
from caf_extractor import caf_to_pcm

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract the WAV contained in a CAF")
    parser.add_argument("src", metavar="source", type=str, help="path to the CAF file")
    parser.add_argument("dest", metavar="destination", type=str, help="path to write the WAV to")
    args = parser.parse_args()
    with open(args.src, "rb") as caf_file:
        with open(args.dest, "wb") as wav_file:
            caf_to_pcm.write_caf_to_wav(caf_file, wav_file)
