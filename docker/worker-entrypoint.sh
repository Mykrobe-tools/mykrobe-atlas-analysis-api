#!/usr/bin/env bash
set -e

./bwa index $REFERENCE_FILEPATH
./samtools faidx $REFERENCE_FILEPATH

exec "$@"