class SamtoolsStatsParser:
    def __init__(self, stats_raw):
        self.stats = stats_raw.decode().split('\n')

    def get(self, keys):
        values = {}

        for line in self.stats:
            if not line.startswith('SN'):
                continue

            cols = line.split('\t')
            stat = cols[1][:-1]
            if stat in keys:
                values[stat] = cols[2]

        return values
