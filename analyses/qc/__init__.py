from analyses.qc.fastq_qc import fastq_qc

SUPPORTED_FORMATS = ['FASTQ']


class UnsupportedSampleFormat(Exception):
    pass


def is_fastq(infile_path):
    return infile_path.endswith('.fastq')  # TODO: Find a better way


def run_qc(infile_path, ref_path):
    if is_fastq(infile_path):
        return fastq_qc(infile_path, ref_path)
    else:
        raise UnsupportedSampleFormat(f'only {"".join(SUPPORTED_FORMATS)} files are supported')