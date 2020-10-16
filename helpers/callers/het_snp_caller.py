# Copied from Clockwork
# Changes:
# - Remove writing out summary_tsv, per_contig_tsv, filtered_vcf. Instead, grab the number of het snps and return immediately.
# - Remove writing out mpileup result to unfiltered_vcf. Instead, pipe it directly to the het filter.

import logging
import os
import re
import subprocess

import pyfastaq

logger = logging.getLogger(__name__)

adf_regex = re.compile(r"""[\t;]ADF=(?P<adf>[0-9,]+)[\t;]""")
adr_regex = re.compile(r"""[\t;]ADR=(?P<adr>[0-9,]+)[\t;]""")


class HetSnpCaller:
    def __init__(
        self,
        sorted_bam,
        ref_fasta,
        outprefix,
        min_total_depth=4,
        min_second_depth=2,
        max_allele_freq=0.9,
    ):
        self.ref_fasta = os.path.abspath(ref_fasta)
        self.bam = sorted_bam
        self.outprefix = os.path.abspath(outprefix)
        self.min_total_depth = min_total_depth
        self.min_second_depth = min_second_depth
        self.max_allele_freq = max_allele_freq

    @classmethod
    def _vcf_line_is_snp_and_or_het(
        cls, vcf_line, min_total_depth, min_second_depth, max_allele_freq
    ):
        """returns tuple: (chromosome name, is a SNP, is a het SNP)"""
        fields = vcf_line.rstrip().split("\t")

        if "," not in fields[4]:
            return (fields[0], False, False)

        adf_search = adf_regex.search(fields[7])
        adr_search = adr_regex.search(fields[7])
        if None in [adf_search, adr_search]:
            raise Exception("Error! Must have ADF and ADR in info column: " + vcf_line)

        adf_list = [int(x) for x in adf_search.group("adf").split(",")]
        adr_list = [int(x) for x in adr_search.group("adr").split(",")]
        if len(adf_list) != len(adr_list):
            raise Exception("Mismatch in lengths of ADF and ADR lists: " + vcf_line)

        adf_sum = sum(adf_list)
        if adf_sum < min_total_depth:
            return (fields[0], False, False)

        adr_sum = sum(adr_list)
        if adr_sum < min_total_depth:
            return (fields[0], False, False)

        adr_max = max(adr_list)
        adf_max = max(adf_list)

        for i, adf in enumerate(adf_list):
            adr = adr_list[i]

            if (
                adf >= min_second_depth
                and adf / adf_sum <= max_allele_freq
                and adr >= min_second_depth
                and adr / adr_sum <= max_allele_freq
            ):
                return (fields[0], True, True)

        if adf_list[0] < adf_max and adr_list[0] < adr_max:
            return (fields[0], True, False)
        else:
            return (fields[0], False, False)

    @classmethod
    def _filter_vcf_and_count_snps(
        cls,
        bam, ref,
        min_total_depth,
        min_second_depth,
        max_allele_freq,
    ):
        results = {}

        cmd = [
            "samtools", "mpileup", "--skip-indels", "-d", "500", "-t", "INFO/AD,INFO/ADF,INFO/ADR", "-C50", "-uv",
            "-f", ref, bam
        ]

        with subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True) as p:
            for line in p.stdout:
                if line.startswith("#"):
                    continue

                chrom, is_snp, is_het = HetSnpCaller._vcf_line_is_snp_and_or_het(
                    line, min_total_depth, min_second_depth, max_allele_freq
                )
                if chrom not in results:
                    results[chrom] = {x: 0 for x in ["positions", "snps", "hets"]}

                results[chrom]["positions"] += 1
                if is_snp:
                    results[chrom]["snps"] += 1
                if is_het:
                    results[chrom]["hets"] += 1

        return results

    @classmethod
    def _write_reports(cls, snp_data, contig_lengths):
        totals = {x: 0 for x in ["length", "positions", "snps", "hets"]}

        for contig in sorted(contig_lengths):
            totals["length"] += contig_lengths[contig]

            if contig in snp_data:
                for key, number in snp_data[contig].items():
                    totals[key] += number

        if totals["snps"] > 0:
            percent_snps = round(100 * totals["hets"] / totals["snps"], 2)
        else:
            percent_snps = 0

        return totals["hets"]

    def run(self):
        ref_lengths = {}
        pyfastaq.tasks.lengths_from_fai(self.ref_fasta + ".fai", ref_lengths)
        snp_data = HetSnpCaller._filter_vcf_and_count_snps(
            self.bam, self.ref_fasta,
            self.min_total_depth,
            self.min_second_depth,
            self.max_allele_freq,
        )

        return HetSnpCaller._write_reports(snp_data, ref_lengths)