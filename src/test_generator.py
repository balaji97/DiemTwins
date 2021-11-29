import itertools
import os
import random
import shutil
from collections import defaultdict

import generate_partitions

from generator_models import JsonObject


# Generate all the possible leader-partition pairs
def generate_leader_partitions(partition_scenarios, all_validators, leader_type):
    leader_partitions_pair = []

    all_validator_ids = set()
    [all_validator_ids.update(partition) for partition in partition_scenarios[0]]

    faulty_validators_id_list = [validatorId.split("_")[0] for validatorId in all_validator_ids if len(validatorId.split("_")) > 1]

    for partition in partition_scenarios:
        for validator in all_validators:
            if leader_type == "ALL":
                leader_partitions_pair.append((validator, partition))

            elif leader_type == "FAULTY" and validator in faulty_validators_id_list:
                leader_partitions_pair.append((validator, partition))

            elif leader_type == "NON-FAULTY" and validator not in faulty_validators_id_list:
                leader_partitions_pair.append((validator, partition))
    print("STEP 2", len(leader_partitions_pair))
    return leader_partitions_pair

def getMsgTypeCombinations():
    msg_types = ["VOTE", "PROPOSAL"]
    all_combinations = []
    for num_subset in range(0, len(msg_types) + 1):
        for comb in itertools.combinations(msg_types, num_subset):
            all_combinations.append(list(comb))
    return all_combinations


def getDropConfig():
    all_drop_permutations = getMsgTypeCombinations()
    random.shuffle(all_drop_permutations)
    return all_drop_permutations[0]


def generateDropConfig(round_num_list, partition_size):
    dropConfig = defaultdict(list)
    if round_num_list is None:
        return dropConfig

    for round_num in round_num_list:
        for partition in range(partition_size):
            dropConfig[round_num].append(getDropConfig())
    return dropConfig


# Combine rounds with leader-partition pairs with and without replacement.
def generate_leader_partitions_with_rounds(all_leader_partitions, num_rounds, n_testcases, is_deterministic,
                                              isWithReplacement, partition_size,n_twins, validator_twin_ids, n_validators,batch_size):

    round_leader_partition_pairs = []
    total_leader_partition = len(all_leader_partitions)
    index_list = list(range(total_leader_partition))

    if not is_deterministic:
        random.shuffle(index_list)
    count_testcases = 0

    flag = False
    if not isWithReplacement:
        all_round_combinations = list(itertools.combinations(index_list, num_rounds))
        # print("comb", len(all_round_combinations))
        for each_combination in all_round_combinations:
            all_permutations = list(itertools.permutations(each_combination))
            # print("all_permutations ",all_permutations)
            for permutation in all_permutations:
                round_leader_partition_pairs.append(accumulate(permutation, all_leader_partitions, num_rounds, partition_size, n_twins, validator_twin_ids, n_validators))
                count_testcases += 1

                if count_testcases == n_testcases:
                    flag = True

                if not flag and len(round_leader_partition_pairs) == batch_size:
                    dump_file(round_leader_partition_pairs, count_testcases)
                    round_leader_partition_pairs = []

                elif flag and round_leader_partition_pairs:
                    dump_file(round_leader_partition_pairs, count_testcases)
                    break

            if flag:
                break
    else:
        permutations = [[] for i in range(total_leader_partition ** num_rounds)]
        all_round_combinations_with_replacement = permutations_with_replacement(total_leader_partition, num_rounds, permutations)
        for permutation in all_round_combinations_with_replacement:
            round_leader_partition_pairs.append(accumulate(permutation, all_leader_partitions, num_rounds, partition_size, n_twins, validator_twin_ids, n_validators))

            if count_testcases == n_testcases:
                flag = True

            if not flag and len(round_leader_partition_pairs) == batch_size:
                dump_file(round_leader_partition_pairs, count_testcases)
                round_leader_partition_pairs = []

            elif flag and round_leader_partition_pairs:
                dump_file(round_leader_partition_pairs, count_testcases)
                break
            count_testcases += 1

    print("STEP 3: ", len(round_leader_partition_pairs))


def permutations_with_replacement(n, k, permutations):
    m = 0
    if k < 1:
        return permutations

    for i in range(27):
        permutations[i].append(m % n)
        if (i % n ** (k - 1)) == n ** (k - 1) - 1:
            m = m + 1

    return permutations_with_replacement(n, k - 1, permutations)


def pad(l, size, padding):
    return l + [padding] * abs((len(l) - size))


def get_next_sample(s, num_rounds):
    sample = s[-num_rounds:]
    del s[-num_rounds:]
    sample = pad(sample, num_rounds, sample[-1])
    return sample, s


def accumulate(index_list, leader_partition_pairs, n_rounds, partition_size, n_twins, validator_twin_ids, n_validators):
    random_intra_partition_rule_rounds = random.sample(list(range(n_rounds)), random.randint(0, n_rounds))
    drop_config = generateDropConfig(random_intra_partition_rule_rounds, partition_size)

    candidate_configurations = [leader_partition_pairs[idx] for idx, item in enumerate(leader_partition_pairs) if
                                idx in list(index_list)]

    curr_test_case = JsonObject(n_validators, n_twins, n_rounds, partition_size,
                                validator_twin_ids, drop_config, candidate_configurations)

    return curr_test_case.toJSON()


# Writes the list of JSON elements to file
def dump_file(elements, file_count):
    file_name: str = "../testcases/testcases_batch_" + str(file_count) + ".jsonl"

    with open(file_name, "wb") as outfile:
        for element in elements:
            if element is not None:
                outfile.write(element.encode() + b"\n")


def main():
    # Clear testcase directory
    if os.path.exists('../testcases/') and os.path.isdir('../testcases/'):
        shutil.rmtree('../testcases/')

    os.makedirs("../testcases/")

    x = generate_partitions.get_all_possible_partitions(["0", "1", "2", "3", "3_twin"], 2)

    c = generate_leader_partitions(x, ["0", "1", "2", "3", "3_twin"], "FAULTY")

    generate_leader_partitions_with_rounds(all_leader_partitions=c, num_rounds=4, is_deterministic=True,isWithReplacement=False, partition_size=2,n_testcases=50, batch_size=20, n_twins=1,
                                                 validator_twin_ids=[3], n_validators=4)

if __name__ == "__main__":
    main()
