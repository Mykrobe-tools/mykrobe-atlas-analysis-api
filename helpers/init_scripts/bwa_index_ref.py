import subprocess


def bwa_index_ref(reference_filepath):
    subprocess.check_output([
        "./bwa", "index",
        reference_filepath
    ])