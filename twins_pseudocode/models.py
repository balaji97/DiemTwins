from typing import List


class TestConfig:
    # Number of test cases to generate
    n_testcases: int
    # Number of rounds in a test case
    n_rounds: int
    # Number of validators for the BFT
    n_validators: int
    # Number of validators that will have a twin
    n_twins: int
    # Maximum number of network partitions that will be created
    n_partitions: int
    # Maximum number of message types that can be dropped intra-partition
    n_intra_drop_types: int
    # Whether to generate test cases deterministically or not
    is_deterministic: bool
    # Whether to repeat the same leader-partition scenario within a test case
    is_with_replacement: bool
    # Seed for random number generator used for test cases
    seed: int
    # Path at which we store the generated test cases
    path: str


class Partition:
    # Types of messages from {ProposalMessage, VoteMessage, TimeoutMessage} that will be dropped
    # within this partition
    dropped_messages: List[str]
    # List of twin_ids of validators that are a part of the network partition
    partitions: List[str]


class LeaderPartition:
    # Leader for that round
    leader: int
    # List of network partitions for this LeaderPartition scenario
    partitions: List[Partition]


class TestCase:
    # Number of rounds in the test case
    n_rounds: int
    # Number of validators for the BFT
    n_validators: int
    # List of leader-partition combinations described in Step 2 of section 4.2 in the twins paper
    leader_partitions: List[LeaderPartition]
    # List of validator IDs that have a twin
    twin_ids: List[int]
