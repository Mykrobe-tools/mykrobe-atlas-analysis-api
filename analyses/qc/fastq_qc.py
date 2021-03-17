import os
import subprocess
import time
from concurrent.futures.thread import ThreadPoolExecutor

from tracking_client import QcResult

from analyses.tracking import EventName, record_event
from config import SAMTOOLS_VERSION
from helpers import samtools
from helpers.bwa import map_reads
from helpers.callers import het_snp_caller
from helpers.grepers import grep_samstats

COVERAGE_THRESHOLD = os.getenv('COVERAGE_THRESHOLD', 15)
NUM_TB_BASE_PAIRS = os.getenv('NUM_TB_BASE_PAIRS', 4411532)
MAX_HET_SNPS = os.getenv('MAX_HET_SNPS', 100000)


def fastq_qc(infile_paths, sample_id, ref_path, outdir):
    sam_path = map_reads(infile_paths, sample_id, ref_path, outdir)

    with ThreadPoolExecutor() as executor:
        coverage_task = executor.submit(calculate_coverage, sam_path, ref_path, sample_id)
        het_snps_task = executor.submit(calculate_het_snps, sam_path, ref_path, outdir, sample_id)
    coverage = coverage_task.result()
    number_of_het_snps = het_snps_task.result()

    decision = 'passed'
    if coverage <= COVERAGE_THRESHOLD or number_of_het_snps > MAX_HET_SNPS:
        decision = 'failed'

    return QcResult(
        coverage=coverage,
        decision=decision,
        number_of_het_snps=number_of_het_snps
    )


def calculate_het_snps(sam_path, ref_path, outdir, sample_id):
    sorted_sam_path = samtools.sort(sam_path, sample_id)
    hsc = het_snp_caller.HetSnpCaller(
        sorted_sam_path, ref_path, os.path.join(outdir, "het_snps"), sample_id
    )
    return hsc.run()


def calculate_coverage(sam_path, ref_path, sample_id):
    """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/samtools_qc.py#L28
    """
    keys = ['bases mapped (cigar)']
    cmd = ["samtools", "stats", "-r", ref_path, sam_path]

    start_time = time.time()
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True) as samstats_proc:
        samtools_stats = grep_samstats(samstats_proc.stdout, keys)
    duration = int((time.time() - start_time) * 1000)

    record_event(sample_id, EventName.QC, software='samtools', software_version=SAMTOOLS_VERSION,
                 start_timestamp=start_time, duration=duration, command=' '.join(cmd))

    bases_mapped_cigar = int(samtools_stats[keys[0]])
    return bases_mapped_cigar / NUM_TB_BASE_PAIRS