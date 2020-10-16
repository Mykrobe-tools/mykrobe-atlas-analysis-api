from analyses.qc.fastq_qc import fastq_qc

SUPPORTED_FORMATS = ['FASTQ']


class UnsupportedSampleFormat(Exception):
    pass


def is_fastq(infile_path):
    # TODO: Find a better way
    return infile_path.endswith('.fastq') \
        or infile_path.endswith('.fastq.gz')


def run_qc(infile_path, sample_id, ref_path, outdir):
    if is_fastq(infile_path):
        return fastq_qc(infile_path, sample_id, ref_path, outdir)
    else:
        raise UnsupportedSampleFormat(f'only {"".join(SUPPORTED_FORMATS)} files are supported')