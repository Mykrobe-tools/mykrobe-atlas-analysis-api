import sys
import mmh3
import pickle

KMER_SIZE = 31
NUM_HAHES = 1
BLOOMFILTER_SIZE = 28000000
COMPLEMENT = {"A": "T", "C": "G", "G": "C", "T": "A"}


def _seq_to_kmers(seq):
    return [seq[i : i + KMER_SIZE] for i in range(len(seq) - KMER_SIZE + 1)]


def _convert_kmers(kmers):
    converted = []
    for kmer in kmers:
        l = [kmer, "".join([COMPLEMENT.get(base, base) for base in reversed(kmer)])]
        l.sort()
        converted.append(l[0])
    return converted


def _generate_hash(kmer):
    return mmh3.hash(kmer, 0) % BLOOMFILTER_SIZE


def _kmers_to_hahes(kmers):
    return [_generate_hash(kmer) for kmer in kmers]


def _seq_to_hashes(seq):
    return _kmers_to_hahes(_convert_kmers(_seq_to_kmers(seq)))


hashes = []
with open("probes.fa") as fa:
    while True:
        line_ref_seq_name = fa.readline()
        if not line_ref_seq_name:
            break
        line_ref_seq = fa.readline()
        if not line_ref_seq:
            sys.exit("probes.fa ends with ref sequence name but there is no ref sequence")
        ref_seq_hashes = _seq_to_hashes(line_ref_seq.strip())
        hashes.extend(ref_seq_hashes)

        line_alt_seq_name = fa.readline()
        if not line_alt_seq_name:
            sys.exit("probes.fa ends with ref sequence but there is no matched alt sequence")
        line_alt_seq = fa.readline()
        if not line_alt_seq:
            sys.exit("probes.fa ends with alt sequence name but there is no alt sequence")
        alt_seq_hashes = _seq_to_hashes(line_alt_seq.strip())
        hashes.extend(alt_seq_hashes)

with open("probes.hashes.pickle", "wb") as h:
    pickle.dump(hashes, h)
