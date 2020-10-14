import os
import subprocess

from helpers import load_json


class QCTaskManager:
    def __init__(self, reference_filepath, outdir):
        self.outdir = outdir
        self.reference_filepath = reference_filepath

    def qc_filepath(self, sample_id):
        return os.path.join(
            self.outdir, "{sample_id}_qc.json".format(sample_id=sample_id)
        )

    def sam_filepath(self, sample_id):
        return os.path.join(
            self.outdir, "{sample_id}.sam".format(sample_id=sample_id)
        )

    def map_reads(self, file, sample_id):
        """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/read_map.py#L51
        """

        # Must index the ref first
        # Docs: http://bio-bwa.sourceforge.net/bwa.shtml
        subprocess.check_output([
            "./bwa", "index",
            self.reference_filepath
        ])

        with open(self.sam_filepath(sample_id), 'w') as outfile:
            subprocess.check_call([
                "./bwa", "mem",
                self.reference_filepath, file
            ], stdout=outfile)

    def run_qc(self, file, sample_id):
        """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/samtools_qc.py#L28
        """
        self.map_reads(file, sample_id)

        outfile = self.qc_filepath(sample_id)
        subprocess.check_output([
            "./samtools",
            # "predict",
            # sample_id,
            # "tb",
            # "-1",
            # file,
            # "--format",
            # "json",
            # "--tmp",
            # self.outdir,
            # "--skeleton_dir",
            # self.skeleton_dir,
            # "--output",
            # outfile,
        ])

        # Load the output
        results = load_json(outfile)

        return results
