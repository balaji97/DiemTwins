import itertools
import random

import generate_partitions

from models import TestConfig

msg_types=["VOTE","PROPOSAL"]


def generate_test_case(test_config: TestConfig):
    if test_config.seed is not None:
        random.seed(test_config.seed)

    validator_ids = [i for i in range(1, test_config.n_validators + 1)]
    twin_ids = random.sample(validator_ids, test_config.n_twins)

    # Generate a list of all validators including twins
    validator_twin_ids = [str(validator_id) for validator_id in validator_ids]
    for twin_id in twin_ids:
        validator_twin_ids.append(str(twin_id) + "_twin")

    # Generate all possible partition scenarios as described in Step 1 of 4.2 in the Twins paper
    valid_partition_scenarios = generate_partition_scenarios(validator_twin_ids, test_config.num_non_empty_partition,
                                                             test_config.enum_limit)

    # Generates all possible leader partitions as described in Step 2 of 4.2 in the Twins paper
    all_leader_partitions = generate_leader_partitions(valid_partition_scenarios, validator_ids,
                                                       test_config.leader_type, test_config.enum_limit)

    all_leader_partitions_round_wise = generate_leader_partitions_with_rounds(all_leader_partitions,
                                                        test_config.n_rounds, test_config.is_deterministic, test_config.is_with_replacement)


# def getIdxForMaxlen(partition):
#     idx = 0
#     curr_len = 0
#     for _idx, item in enumerate(partition):
#         if len(item) > curr_len:
#             curr_len = len(item)
#             idx = _idx
#     return idx


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

    return leader_partitions_pair


def generate_leader_partitions_with_rounds(all_leader_partitions, n_rounds, is_deterministic, with_replacement):
    all_leader_partition_pairs_round_wise = []
    round_num = 0
    leader_partition_pair_idx = 0
    while round_num < n_rounds:
        all_leader_partition_pairs_round_wise.append(all_leader_partitions[leader_partition_pair_idx])
        leader_partition_pair_idx = (leader_partition_pair_idx + 1) % len(all_leader_partitions)
        round_num += 1

    if not is_deterministic:
        random.shuffle(all_leader_partition_pairs_round_wise)
    return all_leader_partition_pairs_round_wise


def generate_partition_scenarios(validator_ids, num_non_empty_partition, max_partitions, is_deterministic):
    return generate_partitions.getAllPossiblePartitions(validator_ids, num_non_empty_partition, max_partitions, is_deterministic)


def getAllCombinations(self):
    all_combinations = []
    stuff = msg_types
    for L in range(0, len(stuff) + 1):
        for subset in itertools.combinations(stuff, L):
            if len(subset) != 0:
                all_combinations.append(subset)
    return all_combinations


def getprobableDropConfig(self ):
    all_permutation = self.getAllCombinations()
    random.shuffle(all_permutation)
    drop_config = [','.join(i) for i in all_permutation]
    return drop_config[0]


def generateDropConfig(self, round_num_list):
    dropConfig = {}
    for round in round_num_list:
        dropConfig[round] = self.getprobableDropConfig()

    return dropConfig


x = (generate_partitions.getAllPossiblePartitions(["1", "2", "3", "4", "3_twin"], 2, 10))
print(generate_leader_partitions(x, True, "FAULTY", 10))


