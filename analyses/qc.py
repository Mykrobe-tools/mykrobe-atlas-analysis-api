import os
import subprocess

from tracking_client import QcResult

from helpers.parsers.samtools_stats import SamtoolsStatsParser


COVERAGE_THRESHOLD = os.getenv('COVERAGE_THRESHOLD', 15)
NUM_TB_BASE_PAIRS = os.getenv('NUM_TB_BASE_PAIRS', 4411532)


class QCTaskManager:
    def __init__(self, reference_filepath, outdir):
        self.outdir = outdir
        self.reference_filepath = reference_filepath

    def map_reads(self, file):
        """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/read_map.py#L51
        """

        return subprocess.check_output([
            "./bwa", "mem",
            self.reference_filepath, file
        ])

    def get_bases_mapped_cigar(self, file):
        """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/samtools_qc.py#L28
                """
        key = 'bases mapped (cigar)'

        sam = self.map_reads(file)
        samstats = subprocess.check_output([
            "./samtools", "stats"
        ], input=sam)

        parser = SamtoolsStatsParser(samstats)
        return parser.get([key])[key]

    def run_qc(self, file):
        """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/samtools_qc.py#L28
        """
        bases_mapped_cigar = int(self.get_bases_mapped_cigar(file))
        coverage = bases_mapped_cigar / NUM_TB_BASE_PAIRS

        decision = 'failed'
        if coverage > COVERAGE_THRESHOLD:
            decision = 'passed'

        return QcResult(
            coverage=coverage,
            decision=decision,
            number_of_het_snps=0
        )
