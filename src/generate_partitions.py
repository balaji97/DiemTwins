fact = [1]
cache = {}

# Returns all possible ways the list of validator IDs can be divided into n_partitions
def get_all_possible_partitions(validator_ids, n_partitions):
    all_possible_partitions = []
    t = int(count_part(len(validator_ids), n_partitions))
    for i in range(t):
        x = gen_part(validator_ids, n_partitions, i)
        all_possible_partitions.append(x)

    return all_possible_partitions

# todo what is this?
def count_part(n, k):
    if k == 1:
        return 1
    key = n, k
    if key in cache:
        return cache[key]
    t = 0
    for y in range(0, n - k + 1):
        t += count_part(n - 1 - y, k - 1) * n_choose_k(n - 1, y)

    cache[key] = t
    return t

# todo what is this?
def gen_part(A, k, i):
    if k == 1:
        return [A]
    n = len(A)
    for y in range(0, n - k + 1):
        extra = count_part(n - 1 - y, k - 1) * n_choose_k(n - 1, y)
        if i < extra:
            break
        i -= extra
    count_partition, count_subset = divmod(i, n_choose_k(n - 1, y))
    subset = [A[0]] + ith_subset(A[1:], y, count_subset)
    S = set(subset)
    return [subset] + gen_part([a for a in A if a not in S], k - 1, count_partition)


# Returns the value of (n choose k)
def n_choose_k(n, k):
    while len(fact) <= n:
        fact.append(fact[-1] * len(fact))
    return fact[n] / (fact[k] * fact[n - k])

# todo what is this?
def ith_subset(a, k, i):
    n = len(a)
    if n == k:
        return a
    if k == 0:
        return []
    for x in range(n):
        extra = n_choose_k(n - x - 1, k - 1)
        if i < extra:
            break
        i -= extra

    return [a[x]] + ith_subset(a[x + 1:], k - 1, i)
