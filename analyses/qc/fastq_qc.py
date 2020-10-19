import os
import subprocess

from tracking_client import QcResult

from helpers.bwa import map_reads
from helpers.callers import het_snp_caller
from helpers.grepers import grep_samstats

COVERAGE_THRESHOLD = os.getenv('COVERAGE_THRESHOLD', 15)
NUM_TB_BASE_PAIRS = os.getenv('NUM_TB_BASE_PAIRS', 4411532)
MAX_HET_SNPS = os.getenv('MAX_HET_SNPS', 100000)


def fastq_qc(infile_paths, sample_id, ref_path, outdir):
    sam_path = map_reads(infile_paths, sample_id, ref_path, outdir)

    coverage = calculate_coverage(sam_path, ref_path)
    number_of_het_snps = calculate_het_snps(sam_path, ref_path, outdir)

    decision = 'passed'
    if coverage <= COVERAGE_THRESHOLD or number_of_het_snps > MAX_HET_SNPS:
        decision = 'failed'

    return QcResult(
        coverage=coverage,
        decision=decision,
        number_of_het_snps=number_of_het_snps
    )


def calculate_het_snps(sam_path, ref_path, outdir):
    hsc = het_snp_caller.HetSnpCaller(
        sam_path, ref_path, os.path.join(outdir, "het_snps")
    )
    return hsc.run()


def calculate_coverage(sam_path, ref_path):
    """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/samtools_qc.py#L28
    """
    keys = ['bases mapped (cigar)']

    with subprocess.Popen([
        "samtools", "stats", "-f", ref_path, sam_path
    ], stdout=subprocess.PIPE, universal_newlines=True) as samstats_proc:
        samtools_stats = grep_samstats(samstats_proc.stdout, keys)

    bases_mapped_cigar = int(samtools_stats[keys[0]])
    return bases_mapped_cigar / NUM_TB_BASE_PAIRS