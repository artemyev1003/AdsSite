def naturalsize(count):
    fcount = float(count)
    k = 1024
    m = k ** 2
    g = k * m

    if fcount < k:
        return str(count) + 'B'
    if k <= fcount < m:
        return str(int(fcount / k)) + 'KB'
    if m <= fcount < g:
        return str(int(fcount / m)) + 'MB'
    return str(int(fcount / g)) + 'GB'