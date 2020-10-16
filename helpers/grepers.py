def grep_samstats(pipe, keys):
    column_names = [k + ':' for k in keys]
    values = grep(pipe, column_names.copy(), 'SN', '\t', 1, 2)

    for k, c in zip(keys, column_names):
        values[k] = values[c]
    for c in column_names:
        values.pop(c)

    return values


def grep(pipe, column_names, line_prefix, sep, key_col_idx, value_col_idx):
    values = {}

    for line in pipe:
        if not column_names:
            break

        if not line.startswith(line_prefix):
            continue

        cols = line.split(sep)
        key = cols[key_col_idx]
        if key in column_names:
            values[key] = cols[value_col_idx]
            column_names.remove(key)

    return values