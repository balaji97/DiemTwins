fact = [1]
cache = {}

def getAllPossiblePartitions(validator_ids, partition_size):
    all_Possible_Partitions = []
    t = int(count_part(len(validator_ids), partition_size))
    for i in range(t):
        x = gen_part(validator_ids, partition_size, i)
        all_Possible_Partitions.append(x)
    print("STEP 1", len(all_Possible_Partitions))
    return all_Possible_Partitions


def count_part(n, k):
    if k == 1:
        return 1
    key = n, k
    if key in cache:
        return cache[key]
    t = 0
    for y in range(0, n - k + 1):
        t += count_part(n - 1 - y, k - 1) * nCr(n - 1, y)
    cache[key] = t
    return t


def gen_part(A, k, i):
    if k == 1:
        return [A]
    n = len(A)
    for y in range(0, n - k + 1):
        extra = count_part(n - 1 - y, k - 1) * nCr(n - 1, y)
        if i < extra:
            break
        i -= extra
    count_partition, count_subset = divmod(i, nCr(n - 1, y))
    subset = [A[0]] + ith_subset(A[1:], y, count_subset)
    S = set(subset)
    return [subset] + gen_part([a for a in A if a not in S], k - 1, count_partition)


def nCr(n, k):
    while len(fact) <= n:
        fact.append(fact[-1] * len(fact))
    return fact[n] / (fact[k] * fact[n - k])


def ith_subset(A, k, i):
    n = len(A)
    if n == k:
        return A
    if k == 0:
        return []
    for x in range(n):
        extra = nCr(n - x - 1, k - 1)
        if i < extra:
            break
        i -= extra
    return [A[x]] + ith_subset(A[x + 1:], k - 1, i)
