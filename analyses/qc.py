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

    def get_bases_mapped_cigar(self, file, sample_id):
        """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/samtools_qc.py#L28
                """
        key = 'bases mapped (cigar)'

        self.sam = self.map_reads(file, sample_id)
        self.samstats = subprocess.check_output([
            "./samtools", "stats"
        ], input=self.sam)

        parser = SamtoolsStatsParser(self.samstats)
        return parser.get([key])[key]

    def run_qc(self, file, sample_id):
        """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/samtools_qc.py#L28
        """
        qc_result = QcResult()
        qc_result.coverage = self.get_bases_mapped_cigar(file, sample_id)

        if qc_result.coverage / float(4411532) <= 15:
            qc_result.decision = 'failed'
        else:
            qc_result.decision = 'passed'

        return qc_result
