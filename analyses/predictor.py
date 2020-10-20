from helpers import load_json
import subprocess
import os


class PredictorTaskManager:
    def __init__(self, outdir, skeleton_dir):
        self.outdir = outdir
        self.skeleton_dir = skeleton_dir

    def predictor_filepath(self, sample_id):
        return os.path.join(
            self.outdir, "{sample_id}_predictor.json".format(sample_id=sample_id)
        )

    def run_predictor(self, files, sample_id):
        outfile = self.predictor_filepath(sample_id)
        out = subprocess.check_output(
            [
                "mykrobe",
                "predict",
                sample_id,
                "tb",
                "-1",
            ] + files + [
                "--format",
                "json",
                "--tmp",
                self.outdir,
                "--skeleton_dir",
                self.skeleton_dir,
                "--output",
                outfile,
            ]
        )
        ## Load the output
        results = load_json(outfile)
        return results
