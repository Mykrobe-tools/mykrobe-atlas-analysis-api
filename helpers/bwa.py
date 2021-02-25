import subprocess
import time
from pathlib import Path

from analyses.tracking import EventName, record_event
from config import BWA_VERSION


def map_reads(infile_paths, sample_id, reference_filepath, outdir, read_group=None):
    """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/read_map.py#L51
    """
    outpath = Path(outdir) / f'{sample_id}.sam'

    # "LB:LIB" is needed, otherwise samtools rmdup segfaults when map_reads_set() is used
    R_option = [] if read_group is None else [
        r"""-R '@RG\tLB:LIB\tID:"""
        + read_group[0]
        + r"""\tSM:"""
        + read_group[1]
        + "'"
    ]

    cmd = ["bwa", "mem", "-M"] + R_option + [reference_filepath] + infile_paths
    awk_cmd = ["awk", "/^@/ || !and($2,256)"]  # remove secondary alignments (but keep header)

    start_time = time.time()
    with open(outpath, 'wb') as outfile:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE) as p1:
            subprocess.run(awk_cmd, stdin=p1.stdout, stdout=outfile)
    duration = int((time.time() - start_time) * 1000)

    record_event(sample_id, EventName.QC, software='bwa', software_version=BWA_VERSION,
                 start_timestamp=start_time, duration=duration, command=' '.join(cmd))

    return outpath