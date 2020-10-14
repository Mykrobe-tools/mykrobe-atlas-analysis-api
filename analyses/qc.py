import subprocess

from tracking_client import QcResult

from helpers.parsers.samtools_stats import SamtoolsStatsParser


class QCTaskManager:
    def __init__(self, reference_filepath, outdir):
        self.outdir = outdir
        self.reference_filepath = reference_filepath
        self.sam = b''
        self.samstats = b''

    def map_reads(self, file, sample_id):
        """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/read_map.py#L51
        """

        return subprocess.check_output([
            "./bwa", "mem",
            self.reference_filepath, file
        ])

    def run_qc(self, file, sample_id):
        """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/samtools_qc.py#L28
        """
        keys = ['bases mapped (cigar)']

        self.sam = self.map_reads(file, sample_id)
        self.samstats = subprocess.check_output([
            "./samtools", "stats"
        ], input=self.sam)

        parser = SamtoolsStatsParser(self.samstats)
        values = parser.get(keys)

        return QcResult(coverage=values[0])
