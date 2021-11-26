import random

# Generates a TestCase for an input test_config from the user
from twins_pseudocode.models import TestCase, LeaderPartition, TestConfig
from twins_pseudocode import generate_partitions

def generate_test_case(test_config: TestConfig):
    # Applies seed if present
    if test_config.seed is not None:
        random.seed(test_config.seed)

    validator_ids = [i for i in range(1, test_config.n_validators + 1)]
    twin_ids = random.sample(validator_ids, test_config.n_twins)

    # Generate a list of all validators including twins
    validator_twin_ids = [str(validator_id) for validator_id in validator_ids]
    for twin_id in twin_ids:
        validator_twin_ids.append(str(twin_id) + "_twin")

    # Generate all possible partition scenarios as described in Step 1 of 4.2 in the Twins paper
    partition_scenarios = generate_partition_scenarios(validator_twin_ids, 2, test_config.n_partitions)
    # For each partition scenario, enumerate all possible intra-partition message drop scenarios
    # partition_scenarios = enumerate_partition_scenarios_with_drops(
    #     partition_scenarios, test_config.n_intra_drop_types)
    # Generates all possible leader partitions as described in Step 2 of 4.2 in the Twins paper
    all_leader_partitions = generate_leader_partitions(partition_scenarios, validator_twin_ids)
    # Combine the input parition-leader scenarios with rounds as described in Step 3 of 4.2 in the Twins paper
    all_leader_partitions_roundwise = generate_leader_partitions_with_rounds(all_leader_partitions,
                                                                             test_config.n_rounds)

    # Generates leader_partition_permutations deterministically or randomly based on config
    if test_config.is_deterministic:
        leader_partition_permutations = enumerate_test_cases(
            all_leader_partitions, test_config.n_rounds, test_config.n_testcases)
    else:
        leader_partition_permutations = randomly_generate_test_cases(
            all_leader_partitions, test_config.n_rounds, test_config.n_testcases)

    # Wraps each leader_partition_permutation into a TestCase object
    test_cases = [
        TestCase(test_config.n_rounds, test_config.n_validators, leader_partition_permutation, twin_ids)
        for leader_partition_permutation in leader_partition_permutations]

    # Save all testcases to a file
    write_to_file(test_cases, test_config.path)


# Enumerates all possible ways of permuting n_rounds number of leader_partitions
# with replacement. Terminates when we have generated n_rounds worth of permutations
def enumerate_test_cases(leader_partitions, n_rounds, n_testcases):
    # todo
    return []


# Enumerates n_testcases number of leader_partition selection over n_rounds by random selection.
# For each test case, we pick n_rounds number of leader_partition with replacement
def randomly_generate_test_cases(leader_partitions, n_rounds, n_testcases):
    return [[random.choice(leader_partitions) for _ in range(n_rounds)] for _ in range(n_testcases)]


def generate_leader_partitions(partition_scenarios, all_validator_ids):
    leader_partitions = []
    for partition_scenario in partition_scenarios:
        for leader in all_validator_ids:
            # For every partition scenario, enumerate with all possible leaders
            leader_partition = LeaderPartition()
            leader_partition.leader = leader
            leader_partition.partitions = partition_scenario
            leader_partitions.append(leader_partition)

    return leader_partitions

def generate_leader_partitions_with_rounds(all_leader_partitions, n_rounds):
    return []

# Returns a list of all possible partition pairs using a process similar to
# solving the Stirling Number of Second Kind problem.
# A piece of code to achieve the same can be found at
# https://stackoverflow.com/questions/45829748/python-finding-random-k-subset-partition-for-a-given-list
# validator_ids: All the validator ids.
# partition_size: size of each partition
# max_partitions: maximum number of partitions
def generate_partition_scenarios(validator_ids, partition_size, max_partitions):
    return generate_partitions.getAllPossiblePartitions(validator_ids, partition_size, max_partitions)


# Returns a list of partitions after considering every partition to have up to n_message_drop_types
# dropped intra-partition
def enumerate_partition_scenarios_with_drops(partition_scenarios, n_message_drop_types):
    return []


# Writes the generated test_cases to a file at the specified path
def write_to_file(test_cases, path):
    # todo
    pass