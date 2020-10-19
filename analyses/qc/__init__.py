from analyses.qc.fastq_qc import fastq_qc
from config import REFERENCE_FILEPATH, DEFAULT_OUTDIR

SUPPORTED_FORMATS = ['FASTQ']


class UnsupportedSampleFormat(Exception):
    pass


def is_fastq(infile_path):
    # TODO: Find a better way
    return infile_path.endswith('.fastq') \
        or infile_path.endswith('.fastq.gz')


def run_qc(infile_paths, sample_id, ref_path=REFERENCE_FILEPATH, outdir=DEFAULT_OUTDIR):
    if all([is_fastq(p) for p in infile_paths]):
        return fastq_qc(infile_paths, sample_id, ref_path, outdir)
    else:
        raise UnsupportedSampleFormat(f'only {"".join(SUPPORTED_FORMATS)} files are supported')