import os
import subprocess

from tracking_client import QcResult

from helpers.callers import het_snp_caller
from helpers.grepers import grep_samstats

COVERAGE_THRESHOLD = os.getenv('COVERAGE_THRESHOLD', 15)
NUM_TB_BASE_PAIRS = os.getenv('NUM_TB_BASE_PAIRS', 4411532)
MAX_HET_SNPS = 100000


def fastq_qc(infile_path, ref_path):
    sam = map_reads(infile_path, ref_path)

    coverage = calculate_coverage(sam)

    number_of_het_snps = get_number_of_het_snps(sam, ref_path)

    decision = 'passed'
    if coverage <= COVERAGE_THRESHOLD or number_of_het_snps > MAX_HET_SNPS:
        decision = 'failed'

    return QcResult(
        coverage=coverage,
        decision=decision,
        number_of_het_snps=number_of_het_snps
    )


def map_reads(infile_path, reference_filepath):
    """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/read_map.py#L51
    """

    return subprocess.check_output([
        "./bwa", "mem",
        reference_filepath, infile_path
    ])


def get_number_of_het_snps(sam, ref_path):
    hsc = het_snp_caller.HetSnpCaller(
        sam, ref_path, os.path.join(".", "het_snps")
    )
    return hsc.run()


def get_alignment_stats(sam, keys):
    """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/samtools_qc.py#L28
    """

    with subprocess.Popen([
        "./samtools", "stats"
    ], stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True) as samstats_proc:
        # Doing this instead of proc.communicate() because the latter waits for all output to be written out,
        # while we want to process each line as soon as they're out.
        samstats_proc.stdin.write(sam.decode())
        samstats_proc.stdin.close()

        return grep_samstats(samstats_proc.stdout, keys)


def calculate_coverage(sam):
    keys = ['bases mapped (cigar)']
    samtools_stats = get_alignment_stats(sam, keys)
    bases_mapped_cigar = int(samtools_stats[keys[0]])

    return bases_mapped_cigar / NUM_TB_BASE_PAIRS