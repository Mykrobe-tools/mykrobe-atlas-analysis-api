import os
import struct


BASES = {"00": "A", "01": "G", "10": "C", "11": "T"}


def extract_kmers_from_ctx(ctx, k):
    gr = GraphReader(ctx)
    for i in gr:
        for kmer in seq_to_kmers(i.kmer.canonical_value, k):
            yield kmer


def seq_to_kmers(seq, kmer_size):
    for i in range(len(seq) - kmer_size + 1):
        yield seq[i : i + kmer_size]


class GraphReader(object):

    """
    Class to read a cortex graph.
    """

    def __init__(self, graph_file, binary_kmers=False):
        self._file_name = graph_file
        self._file = open(graph_file, "rb")
        self.read_header()
        self.binary_kmers = binary_kmers  # report kmers as bytes

    def read_unsigned_int(self):
        """
        Reads an uint32_t from the stream.
        """
        b = self._file.read(4)
        return struct.unpack("<I", b)[0]

    def read_header(self):
        """
        Reads the header of the graph file.
        """
        magic_str = b"CORTEX"
        b = self._file.read(len(magic_str))
        if b != magic_str:
            raise ValueError("File format mismatch")
        self.version = self.read_unsigned_int()
        if self.version != 6:
            raise ValueError("File format version error; only 6 supported")
        self.kmer_size = self.read_unsigned_int()
        self.kmer_storage_size = 8 * self.read_unsigned_int()
        self.num_colours = self.read_unsigned_int()
        self.record_size = self.kmer_storage_size + 5 * self.num_colours
        # skip per colour mean_read_length and total_sequence
        skip = self.num_colours * 12
        self._file.seek(skip, os.SEEK_CUR)
        for j in range(self.num_colours):
            v = self.read_unsigned_int()
            self._file.seek(v, os.SEEK_CUR)
        # skip per colour error rates
        skip = self.num_colours * 16  # sizeof(long double)
        self._file.seek(skip, os.SEEK_CUR)
        for j in range(self.num_colours):
            # skip cleaning counters
            self._file.seek(12, os.SEEK_CUR)
            v = self.read_unsigned_int()
            self._file.seek(v, os.SEEK_CUR)
        # header ends with the magic word
        b = self._file.read(len(magic_str))
        if b != magic_str:
            raise ValueError("File format mismatch")
        payload_start = self._file.tell()
        self._file.seek(0, os.SEEK_END)
        payload_size = self._file.tell() - payload_start
        self.num_records = payload_size // self.record_size
        self._file.seek(payload_start, os.SEEK_SET)

    def __iter__(self):
        return self

    def __next__(self):
        """
        Returns the next record
        """
        buf = self._file.read(self.record_size)
        if len(buf) == 0:
            raise StopIteration()
        return self.decode_record(buf)

    def next(self):
        # Python 2 compat -
        return self.__next__()

    def decode_record(self, buff):
        """
        Decodes the specified graph record.
        """

        kmer = buff[0:8]  #
        # print(buff[0:8], kmer)
        offset = 8
        coverages = struct.unpack_from("I" * self.num_colours, buff, offset)
        offset += self.num_colours * 4
        edges = struct.unpack_from("B" * self.num_colours, buff, offset)
        # print(edges)
        record = CortexRecord(
            self.kmer_size,
            kmer,
            coverages,
            edges,
            num_colours=self.num_colours,
            binary_kmer=self.binary_kmers,
        )
        return record


class CortexRecord(object):

    """
    Class representing a single record in a cortex graph. A record
    consists of a kmer, its edges and coverages in the colours.
    """

    def __init__(
        self, kmer_size, kmer, coverages, edges, num_colours=1, binary_kmer=False
    ):
        if binary_kmer:
            self.kmer = kmer
        else:
            self.kmer = Kmer(decode_kmer(kmer, kmer_size))
        self.coverages = coverages
        self.edges = [decode_edges(e) for e in edges]
        self.num_colours = num_colours

    def __str__(self):
        return "<CortexRecord %s - %i colour(s)>" % (self.kmer, self.num_colours)

    def print(self, colour):
        nucleotides = "ACGT"
        s = ["." for j in range(8)]
        for j, n in enumerate(nucleotides):
            if n in self.edges[colour][1]:
                s[j] = n.lower()
        for j, n in enumerate(nucleotides):
            if n in self.edges[colour][0]:
                s[j + 4] = n
        s = "".join(s)
        return "{0} {1} {2}".format(self.kmer, self.coverages[colour], s)

    def get_adjacent_kmers(self, colour=0, direction=0):
        """
        Returns the kmers adjacent to this kmer using the edges in the
        record.
        """
        fwd, rev = self.edges[colour]
        if direction == 0:
            for n in fwd:
                yield Kmer(self.kmer.canonical_value[1:] + n)
        else:
            for n in rev:
                yield Kmer(n + self.kmer.canonical_value[:-1])


class Kmer(object):

    """
    A class representing fixed length strings of DNA nucleotides. A Kmer
    is equal to its reverse complement, and the canonical representation
    of a give kmer is the lexically least of itself  and its reverse
    complement.
    """

    def __init__(self, kmer):
        self.value = kmer
        self.canonical_value = canonical_kmer(kmer)

    def __str__(self):
        return self.canonical_value


def decode_kmer(binary_kmer, kmer_size):
    """
    Returns a string representation of the specified kmer.
    """
    # G and C are the wrong way around because we reverse the sequence.
    # This really is a nasty way to do this!
    assert kmer_size <= 31
    binary_kmer_int = struct.unpack("Q", binary_kmer)[0]

    b = "{0:064b}".format(binary_kmer_int)[::-1]
    ret = []
    for j in range(kmer_size):
        nuc = BASES[b[j * 2 : (j + 1) * 2]]
        ret.append(nuc)
    ret = "".join(ret)

    return ret[::-1]


def decode_edges(edges):
    """
    Decodes the specified integer representing edges in Cortex graph. Returns
    a tuple (forward, reverse) which contain the list of nucleotides that we
    append to a kmer and its reverse complement to obtain other kmers in the
    Cortex graph.
    """
    bases = ["A", "C", "G", "T"]
    fwd = []
    for j in range(4):
        if (1 << j) & edges != 0:
            fwd.append(bases[j])
    rev = []
    bases.reverse()
    for j in range(4):
        if (1 << (j + 4)) & edges != 0:
            rev.append(bases[j])
    return fwd, rev


def canonical_kmer(kmer):
    """
    Returns the canonical version of this kmer, which is the lexically
    least of itself and its reverse complement.
    """
    rev = reverse_complement(kmer)
    return rev if rev < kmer else kmer


def reverse_complement(kmer):
    """
    Returns the reverse complement of the specified string kmer.
    """
    d = {"A": "T", "C": "G", "G": "C", "T": "A"}
    # This is very slow and nasty!
    s = ""
    for c in kmer:
        s += d[c]
    return s[::-1]
