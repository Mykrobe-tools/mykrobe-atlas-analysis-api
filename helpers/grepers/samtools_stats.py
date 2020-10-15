class SamtoolsStatsGreper:
    def __init__(self, stats_pipe):
        self.stats_pipe = stats_pipe

    def grep(self, keys):
        values = {}

        for line in self.stats_pipe:
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
