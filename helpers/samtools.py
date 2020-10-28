import subprocess


def sort(sam_path):
    out_path = f"{sam_path}.sorted"
    cmd = ["samtools", "sort", "-o", out_path, sam_path]

    subprocess.run(cmd)

    return out_path