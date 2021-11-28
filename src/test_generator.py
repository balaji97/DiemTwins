import itertools
import random
from collections import defaultdict

import generate_partitions

from generator_models import TestConfig, JsonObject


def generate_test_case(test_config: TestConfig):
    test_cases_count = 0
    validator_ids = [i for i in range(1, test_config.n_validators + 1)]
    twin_ids = random.sample(validator_ids, test_config.n_twins)

    # Generate a list of all validators including twins
    validator_twin_ids = [str(validator_id) for validator_id in validator_ids]
    for twin_id in twin_ids:
        validator_twin_ids.append(str(twin_id) + "_twin")

    # Generate all possible partition scenarios as described in Step 1 of 4.2 in the Twins paper
    valid_partition_scenarios = generate_partition_scenarios(validator_twin_ids, test_config.num_non_empty_partition)

    # Generates all possible leader partitions as described in Step 2 of 4.2 in the Twins paper
    all_leader_partitions = generate_leader_partitions(valid_partition_scenarios, validator_ids,
                                                       test_config.leader_type)

    generate_leader_partitions_with_rounds(all_leader_partitions,
        test_config.n_rounds, test_config.n_testcases, test_config.is_deterministic, test_config.is_with_replacement, test_config.num_non_empty_partition, test_config.n_twins,
        validator_twin_ids, test_config.n_validators, test_config.leader_type, test_config.batch_size, test_cases_count)


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


# Return all the possible partition scenarios
def generate_partition_scenarios(validator_ids, num_non_empty_partition):
    return generate_partitions.getAllPossiblePartitions(validator_ids, num_non_empty_partition)


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

                if count_testcases == n_testcases:
                    flag = True

                if not flag and len(round_leader_partition_pairs) == batch_size:
                    dump_file(round_leader_partition_pairs, count_testcases)
                    round_leader_partition_pairs = []

                elif flag and round_leader_partition_pairs:
                    dump_file(round_leader_partition_pairs, count_testcases)
                    break
                count_testcases += 1
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


def getNextSample(s, num_rounds):
    sample = s[-num_rounds:]
    del s[-num_rounds:]
    sample = pad(sample, num_rounds, sample[-1])
    return sample, s


def accumulate(index_list, leader_partition_pairs, n_rounds, partition_size, n_twins, validator_twin_ids, n_validators):
    random_IntraPartionRuleRounds = random.sample(list(range(n_rounds)), random.randint(0, n_rounds))
    DropConfig = generateDropConfig(random_IntraPartionRuleRounds, partition_size)

    candidate_configurations = [leader_partition_pairs[idx] for idx, item in enumerate(leader_partition_pairs) if
                                idx in list(index_list)]

    curr_test_case = JsonObject(n_validators, n_twins, n_rounds, partition_size,
                                validator_twin_ids, DropConfig, candidate_configurations)

    return curr_test_case.toJSON()


def dump_file(returnList, file_count):
    file_name: str = "testcases_batch_" + str(file_count) + ".jsonl"
    textfile = open(file_name, "wb")
    # file_count += 1
    for element in returnList:
        if element is not None:
            textfile.write(element.encode() + b"\n")
    textfile.close()

# def combine_leader_partition_pairs_with_round(self, leader_partition_pairs_, num_rounds, isDeterministic,
#                                               withReplacement):
#
#     round_leader_partition_pairs = []
#     s = list(range(len(leader_partition_pairs_)))
#
#     if isDeterministic == False:
#         random.shuffle(s)
#
#     returnList = []
#
#     terminate_flag = False
#
#     # sample,s=self.getNextSample(s,len(leader_partition_pairs_),num_rounds)
#
#     if withReplacement == False:
#         all_samples = list(itertools.combinations(s, num_rounds))
#         for sample in all_samples:
#             all_permutations = list(itertools.permutations(sample))
#             # print("all_permutations ",all_permutations)
#             for i in all_permutations:
#                 returnList.append(accumulate(i, leader_partition_pairs_))
#
#                 if len(returnList) == self.batch_size:
#                     dump_file(returnList)
#                     returnList = []
#     else:
#         # print("num_rounds",num_rounds)
#         permutations = [[] for i in range(len(leader_partition_pairs_) ** num_rounds)]
#         print("n", len(leader_partition_pairs_), " k:", num_rounds)
#         all_samples = self.permutations_with_replacement(len(leader_partition_pairs_), num_rounds, permutations)
#         for sample in all_samples:
#             returnList.append(accumulate(sample, leader_partition_pairs_))
#             if len(returnList) == self.batch_size:
#                 self.dump_file(returnList)
#                 returnList = []
#
#         # all_samples = list(itertools.combinations_with_replacement(s, num_rounds))
#     print("len of all_samples", len(all_samples))
#
#     # self.testCaseslimit-=1
#
#     # if self.testCaseslimit==0:
#     #     terminate_flag=True
#     #     break
#
#     # if terminate_flag:
#     #     break
#
#         print("Step 3 ", len(returnList))


x = (generate_partitions.getAllPossiblePartitions(["0", "1", "2", "3", "3_twin"], 2))

c = (generate_leader_partitions(x, ["0", "1", "2", "3", "3_twin"], "FAULTY"))

generate_leader_partitions_with_rounds(all_leader_partitions=c, num_rounds=4, is_deterministic=True,isWithReplacement=False, partition_size=2,n_testcases=100, batch_size=100, n_twins=1,
                                             validator_twin_ids=[3], n_validators=4)

