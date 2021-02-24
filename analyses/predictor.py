import os
import subprocess
import time

from analyses.tracking import record_event, EventName
from config import MYKROBE_VERSION
from helpers import load_json


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
        command = [
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

        start_time = time.time_ns()
        out = subprocess.check_output(command)
        duration = int((time.time_ns() - start_time) / 1000)

        record_event(sample_id, EventName.PREDICTION, software='mykrobe', software_version=MYKROBE_VERSION,
                     start_timestamp=start_time,
                     duration=duration, command=' '.join(command))

        ## Load the output
        results = load_json(outfile)
        return results
