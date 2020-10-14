class SamtoolsStatsParser:
    def __init__(self, stats_file=None, stats_raw=None):
        assert stats_file or stats_raw, 'Either a file or a byte sequence must be provided'

        if stats_file:
            self.stats = stats_file
        else:
            self.stats = stats_raw.decode().split('\n')

    def get(self, keys):
        values = []

        for line in self.stats:
            if not line.startswith('SN'):
                continue

            cols = line.split('\t')
            stat = cols[1][:-1]
            if stat in keys:
                values.append(cols[2])

        return values
