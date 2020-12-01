import subprocess
from time import time

from analyses.tracking import record_event, EventName
from config import SAMTOOLS_VERSION


def sort(sam_path, sample_id):
    out_path = f"{sam_path}.sorted"
    cmd = ["samtools", "sort", "-o", out_path, sam_path]

    start_time = time()
    subprocess.run(cmd)
    duration = time() - start_time

    record_event(sample_id, EventName.QC, software='samtools', software_version=SAMTOOLS_VERSION,
                 start_timestamp=start_time, duration=duration, command=' '.join(cmd))

    return out_path