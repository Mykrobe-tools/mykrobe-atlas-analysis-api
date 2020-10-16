#!/usr/bin/env bash

REF=NC_000962.3.fasta

bwa index $REF
samtools faidx $REF