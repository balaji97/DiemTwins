import sys
import time

sys.path.append("../config/")

import itertools
import os
import random
import shutil

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


# Combine leader-partition pairs with every kind of drop type
def enumerate_leader_partitions_with_drops(leader_partitions, drop_types):
    drop_types = drop_types[:2]
    result = []
    drop_scenarios = [[]]

    if len(drop_types) > 0:
        drop_scenarios.append(drop_types)

    if len(drop_types) > 1:
        drop_scenarios += [[drop_type] for drop_type in drop_types]

    for leader, partition in leader_partitions:
        for drop_scenario in drop_scenarios:
            result.append((leader, partition, drop_scenario))

    return result

# Combine rounds with leader-partition pairs with or without replacement.
def enumerate_leader_partition_pairs_over_rounds(leader_partition_pairs, n_rounds, n_testcases, is_deterministic,
                                                 is_with_replacement, validator_twin_ids, n_validators, batch_size):

    round_leader_partition_pairs = []
    total_leader_partition = len(leader_partition_pairs)
    index_list = list(range(total_leader_partition))

    if not is_with_replacement and is_deterministic:
        all_round_combinations = []

        for each_combination in list(itertools.combinations(index_list, n_rounds)):
            all_round_combinations += list(itertools.permutations(each_combination))
            if len(all_round_combinations) > n_testcases:
                break

    else:
        if is_deterministic:
            permutations = [[] for _ in range(total_leader_partition ** n_rounds)]
            all_round_combinations = permutations_with_replacement(total_leader_partition, n_rounds,
                                                                                    permutations)
        else:
            all_round_combinations = enumerate_randomized(leader_partition_pairs, n_rounds, n_testcases)

    count_testcases = 0
    flag = False

    for permutation in all_round_combinations:
        round_leader_partition_pairs.append(
            accumulate(permutation, leader_partition_pairs, n_rounds, validator_twin_ids, n_validators))
        count_testcases += 1

        if count_testcases == n_testcases:
            flag = True

        if not flag and len(round_leader_partition_pairs) == batch_size:
            dump_file(round_leader_partition_pairs, count_testcases)
            round_leader_partition_pairs = []

        elif flag and round_leader_partition_pairs:
            dump_file(round_leader_partition_pairs, count_testcases)
            break


# Enumerate n_test_cases ways of randomly arranging leader_partition pairs over n_rounds
def enumerate_randomized(leader_partition_pairs, n_rounds, n_test_cases):
    return [[random.randrange(len(leader_partition_pairs)) for _ in range(n_rounds)] for _ in range(n_test_cases)]


# Return all ways of arranging n leader_partition pairs over k rounds
def permutations_with_replacement(n, k, permutations):
    m = 0
    if k < 1:
        return permutations

    for i in range(27):
        permutations[i].append(m % n)
        if (i % n ** (k - 1)) == n ** (k - 1) - 1:
            m = m + 1

    return permutations_with_replacement(n, k - 1, permutations)


# Convert given testcase into a JSON object
def accumulate(index_list, leader_partition_pairs, n_rounds, validator_twin_ids, n_validators):
    round_leader_partitions = [leader_partition_pairs[idx] for idx in index_list]
    curr_test_case = JsonObject(n_validators, n_rounds, validator_twin_ids, round_leader_partitions)

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

    if 'seed' in generator_config:
        random.seed(generator_config['seed'])

    validator_ids = [validator_id for validator_id in range(generator_config['n_validators'])]
    twin_ids = [validator_id for validator_id in range(generator_config['n_twins'])]
    validator_and_twin_ids = [str(validator_id) for validator_id in validator_ids] \
                + [str(validator_id) + "_twin" for validator_id in twin_ids]

    # Step 1
    start_time = time.time()

    partition_scenarios = generate_partitions.get_all_possible_partitions(
        validator_and_twin_ids, generator_config['n_partitions'], generator_config['generate_valid_partition'],
        generator_config['n_twins'])

    step_1_time = time.time() - start_time

    # Step 2
    start_time = time.time()

    leader_partition_pairs = generate_leader_partitions(
        partition_scenarios, validator_ids, twin_ids, generator_config['allowed_leader_type'])

    # Adding message drops
    leader_partitions_with_drops = enumerate_leader_partitions_with_drops(
        leader_partition_pairs, generator_config['intra_partition_drop_types'])

    step_2_time = time.time() - start_time

    # Step 3
    start_time = time.time()

    enumerate_leader_partition_pairs_over_rounds(leader_partition_pairs=leader_partitions_with_drops,
                                                 n_rounds=generator_config['n_rounds'],
                                                 n_testcases=generator_config['n_testcases'],
                                                 is_deterministic=generator_config['is_deterministic'],
                                                 is_with_replacement=generator_config['is_with_replacement'],
                                                 validator_twin_ids=twin_ids, n_validators=len(validator_ids),
                                                 batch_size=generator_config['test_file_batch_size'])
    step_3_time = time.time() - start_time

    print("Step 1 time taken " + str(step_1_time))
    print("Step 2 time taken " + str(step_2_time))
    print("Step 3 time taken " + str(step_3_time))
    print("Total time taken " + str(step_1_time + step_2_time + step_3_time))


if __name__ == "__main__":
    main()
