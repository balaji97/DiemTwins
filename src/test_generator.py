import itertools
import os
import random
import shutil
from collections import defaultdict

import generate_partitions

from generator_models import JsonObject
from generator_config import generator_config


# Generate all the possible leader-partition pairs
def generate_leader_partitions(partition_scenarios, validator_ids, twin_ids, leader_type):
    leader_partitions_pairs = []

    all_validator_ids = set()
    [all_validator_ids.update(partition) for partition in partition_scenarios[0]]

    faulty_validators_id_list = [validatorId.split("_")[0] for validatorId in all_validator_ids if len(validatorId.split("_")) > 1]

    for partition in partition_scenarios:
        for validator_id in validator_ids:
            if leader_type == "ALL":
                leader_partitions_pairs.append((validator_id, partition))
            elif leader_type == "FAULTY" and validator_id in twin_ids:
                leader_partitions_pairs.append((validator_id, partition))
            elif leader_type == "NON-FAULTY" and validator_id not in faulty_validators_id_list:
                leader_partitions_pairs.append((validator_id, partition))

    return leader_partitions_pairs


# Combine rounds with leader-partition pairs with and without replacement.
def enumerate_leader_partition_pairs_over_rounds(leader_partition_pairs, n_rounds, n_testcases, is_deterministic,
                                                 is_with_replacement, partition_size, validator_twin_ids, n_validators,
                                                 batch_size):

    round_leader_partition_pairs = []
    total_leader_partition = len(leader_partition_pairs)
    index_list = list(range(total_leader_partition))

    if not is_deterministic:
        random.shuffle(index_list)
    count_testcases = 0

    flag = False
    if not is_with_replacement:
        all_round_combinations = list(itertools.combinations(index_list, n_rounds))

        for each_combination in all_round_combinations:
            all_permutations = list(itertools.permutations(each_combination))

            for permutation in all_permutations:
                round_leader_partition_pairs.append(
                    accumulate(permutation, leader_partition_pairs, n_rounds, partition_size, validator_twin_ids,
                               n_validators))
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
        permutations = [[] for i in range(total_leader_partition ** n_rounds)]
        all_round_combinations_with_replacement = permutations_with_replacement(total_leader_partition, n_rounds, permutations)
        for permutation in all_round_combinations_with_replacement:
            round_leader_partition_pairs.append(
                accumulate(permutation, leader_partition_pairs, n_rounds, partition_size, validator_twin_ids,
                           n_validators))
            count_testcases += 1

            if count_testcases == n_testcases:
                flag = True

            if not flag and len(round_leader_partition_pairs) == batch_size:
                dump_file(round_leader_partition_pairs, count_testcases)
                round_leader_partition_pairs = []

            elif flag and round_leader_partition_pairs:
                dump_file(round_leader_partition_pairs, count_testcases)
                break



def generate_drop_config(round_num_list, partition_size):
    drop_config = defaultdict(list)
    if round_num_list is None:
        return drop_config

    for round_num in round_num_list:
        for partition in range(partition_size):
            drop_config[round_num].append(get_drop_config())
    return drop_config


def get_drop_config():
    all_drop_permutations = get_msg_type_combinations()
    random.shuffle(all_drop_permutations)
    return all_drop_permutations[0]


def get_msg_type_combinations():
    msg_types = ["VOTE", "PROPOSAL"]
    all_combinations = []
    for num_subset in range(0, len(msg_types) + 1):
        for comb in itertools.combinations(msg_types, num_subset):
            all_combinations.append(list(comb))
    return all_combinations


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


def accumulate(index_list, leader_partition_pairs, n_rounds, partition_size, validator_twin_ids, n_validators):
    random_intra_partition_rule_rounds = random.sample(list(range(n_rounds)), random.randint(0, n_rounds))
    drop_config = generate_drop_config(random_intra_partition_rule_rounds, partition_size)

    round_leader_partitions = [leader_partition_pairs[idx] for idx, item in enumerate(leader_partition_pairs) if
                                idx in list(index_list)]

    curr_test_case = JsonObject(n_validators, n_rounds, validator_twin_ids, drop_config, round_leader_partitions)

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

    validator_ids = [validator_id for validator_id in range(generator_config['n_validators'])]
    twin_ids = [validator_id for validator_id in range(generator_config['n_twins'])]
    validator_and_twin_ids = [str(validator_id) for validator_id in validator_ids] \
                + [str(validator_id) + "_twin" for validator_id in twin_ids]

    # Step 1
    partition_scenarios = generate_partitions.get_all_possible_partitions(
        validator_and_twin_ids, generator_config['n_partitions'])

    # Step 2
    leader_partition_pairs = generate_leader_partitions(
        partition_scenarios, validator_ids, twin_ids, generator_config['allowed_leader_type'])

    # Step 3
    enumerate_leader_partition_pairs_over_rounds(leader_partition_pairs=leader_partition_pairs,
                                                 n_rounds=generator_config['n_rounds'],
                                                 n_testcases=generator_config['n_testcases'],
                                                 is_deterministic=generator_config['is_deterministic'],
                                                 is_with_replacement=generator_config['is_with_replacement'],
                                                 partition_size=generator_config['n_partitions'],
                                                 validator_twin_ids=twin_ids, n_validators=len(validator_ids),
                                                 batch_size=generator_config['test_file_batch_size'])

if __name__ == "__main__":
    main()
