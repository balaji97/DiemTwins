from typing import List


class TestConfig:
    # Number of rounds in the test case
    n_rounds: int
    # Number of validators for the BFT
    n_validators: int
    # Number of validators that will have a twin
    n_twins: int
    # Maximum number of network partitions that will be created
    n_partitions: int
    # Whether to generate test cases deterministically or not
    is_deterministic: bool
    # Seed for random number generator used for test cases
    seed: int


class LeaderPartition:
    # Leader for that round
    leader: int
    # List of lists. Each nested list represents a partition, which consists of twin_ids of validators that
    # are a part of that network partition
    partitions: List[List]
    # List of messages(ProposalMessage, VoteMessage) that will be dropped within a partition.
    # By default, none of the messages are dropped.
    dropped_messages: List[str]


class TestCase:
    # Number of rounds in the test case
    n_rounds: int
    # Number of validators for the BFT
    n_validators: int
    # List of leader-partition combinations described in Step 2 of section 4.2 in the twins paper
    leader_partitions: List[LeaderPartition]
    # List of validator IDs that have a twin
    twin_ids: List[int]
