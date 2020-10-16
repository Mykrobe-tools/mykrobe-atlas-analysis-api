import subprocess
from pathlib import Path


def map_reads(infile_path, sample_id, reference_filepath, outdir, read_group=None):
    """Ref: https://github.com/iqbal-lab-org/clockwork/blob/7113a9bfd67e1eb7ace4895a48c8e9a255a658e0/python/clockwork/read_map.py#L51
    """
    outpath = Path(outdir) / f'{sample_id}.sam'

    # "LB:LIB" is needed, otherwise samtools rmdup segfaults when map_reads_set() is used
    R_option = (
        "" if read_group is None
        else r"""-R '@RG\tLB:LIB\tID:"""
             + read_group[0]
             + r"""\tSM:"""
             + read_group[1]
             + "'"
    )

    with open(outpath, 'wb') as outfile:
        with subprocess.Popen([
            "./bwa", "mem", "-M",
            R_option,
            reference_filepath, infile_path,
        ], stdout=subprocess.PIPE):
            subprocess.run(["awk", "'/^@/ || !and($2,256)'"], stdout=outfile)

    return outpath