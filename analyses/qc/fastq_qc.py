import os
import subprocess

from tracking_client import QcResult

from helpers.grepers.samtools_stats import SamtoolsStatsGreper

COVERAGE_THRESHOLD = os.getenv('COVERAGE_THRESHOLD', 15)
NUM_TB_BASE_PAIRS = os.getenv('NUM_TB_BASE_PAIRS', 4411532)


def fastq_qc(infile_path, ref_path):
    coverage = calculate_coverage(infile_path, ref_path)

    decision = 'failed'
    if coverage > COVERAGE_THRESHOLD:
        decision = 'passed'

    return QcResult(
        coverage=coverage,
        decision=decision,
        number_of_het_snps=0
    )


def map_reads(infile_path, reference_filepath):
    """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/read_map.py#L51
    """

    return subprocess.check_output([
        "./bwa", "mem",
        reference_filepath, infile_path
    ])


def get_alignment_stats(infile_path, reference_filepath, keys):
    """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/samtools_qc.py#L28
    """

    sam = map_reads(infile_path, reference_filepath)

    with subprocess.Popen([
        "./samtools", "stats"
    ], stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True) as samstats_proc:
        # Doing this instead of proc.communicate() because the latter waits for all output to be written out,
        # while we want to process each line as soon as they're out.
        samstats_proc.stdin.write(sam.decode())
        samstats_proc.stdin.close()

        greper = SamtoolsStatsGreper(samstats_proc.stdout)
        return greper.grep(keys)


def calculate_coverage(infile, ref):
    key = 'bases mapped (cigar)'
    samtools_stats = get_alignment_stats(infile, ref, [key])
    bases_mapped_cigar = int(samtools_stats[key])

    return bases_mapped_cigar / NUM_TB_BASE_PAIRS