#!/usr/bin/env bash
set -e

./bwa index $REFERENCE_FILEPATH

exec "$@"