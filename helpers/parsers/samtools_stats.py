class SamtoolsStatsParser:
    def __init__(self, stats_raw):
        self.stats = stats_raw

    def get(self, keys):
        values = {}

        for line in self.stats:
            if not keys:
                break

            if not line.startswith('SN'):
                continue

            cols = line.split('\t')
            stat = cols[1][:-1]
            if stat in keys:
                values[stat] = cols[2]
                keys.remove(stat)

        return values
