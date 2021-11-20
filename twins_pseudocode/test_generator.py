import random

# Generates a TestCase for an input test_config from the user
from twins.models.models import TestCase, LeaderPartition


def generate_test_case(test_config):
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
    partition_scenarios = generate_partition_scenarios(validator_twin_ids, test_config.max_partitions)
    # For each partition scenario, enumerate all possible intra-partition message drop scenarios
    partition_scenarios = enumerate_partition_scenarios_with_drops(
        partition_scenarios, test_config.n_message_drop_types)
    # Generates all possible leader partitions as described in Step 2 of 4.2 in the Twins paper
    all_leader_partitions = generate_leader_partitions(partition_scenarios, test_config.n_validators)

    # Initializes test_case object
    test_case = TestCase()
    test_case.n_rounds = test_config.n_rounds
    test_case.n_validators = test_config.n_validators
    test_case.twin_ids = twin_ids

    # The leader partition scenarios that we will include in this testcase. Size will be n_rounds
    leader_partitions = []

    # In case it is deterministic, we will be picking from our enumeration of leader partitions
    # from start to end
    if test_config.is_deterministic:
        leader_partition_ptr = 0
    else:
        leader_partition_ptr = None

    # Keeps appending leader_partition to the list until we generate for n_rounds.
    while len(leader_partitions) < test_config.n_rounds:
        # If test case is generated randomly, we use random choice with replacement
        # Else we pick from the first element onwards of all permutations
        if leader_partition_ptr is None:
            leader_partition = random.choice(all_leader_partitions)
        else:
            leader_partition = all_leader_partitions[leader_partition_ptr]
            leader_partition_ptr += 1

        # To ensure some progress in our system, we keep a condition that every 3rd round
        # has to have some sort of Quorum possible
        if has_quorum(leader_partition, test_config.f) or len(leader_partitions) % 3 != 0:
            leader_partitions.append(leader_partition)

    test_case.leader_partitions = leader_partitions
    return test_case


def generate_leader_partitions(partition_scenarios, n_validators):
    leader_partitions = []
    for partition_scenario in partition_scenarios:
        for leader in range(1, n_validators + 1):
            # For every partition scenario, enumerate with all possible leaders
            leader_partition = LeaderPartition()
            leader_partition.leader = leader
            leader_partition.partitions = partition_scenario
            leader_partitions.append(leader_partition)

    return leader_partitions


# Returns a list of all possible partition pairs using a process similar to
# solving the Stirling Number of Second Kind problem.
# A piece of code to achieve the same can be found at
# https://stackoverflow.com/questions/45829748/python-finding-random-k-subset-partition-for-a-given-list
def generate_partition_scenarios(validator_twin_ids, max_partitions):
    return []


# Returns a list of partitions after considering every partition to have up to n_message_drop_types
# dropped intra-partition
def enumerate_partition_scenarios_with_drops(partition_scenarios, n_message_drop_types):
    # todo
    return []

# Checks if the validators in any of the partitions in the leader_partition can form a quorum
def has_quorum(leader_partition, f):
    if len(leader_partition.dropped_messages) > 0:
        return False

    for partition in leader_partition.partitions:
        unique_validators = set()

        for validator_id in partition:
            unique_validators.add(validator_id.lstrip("_twin"))

        if len(unique_validators) >= 2 * f + 1:
            return True

    return False
