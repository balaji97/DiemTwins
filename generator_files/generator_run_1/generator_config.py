generator_config = {
    "n_validators": 4,
    "n_partitions": 2,
    # One of {ALL, NON-FAULTY, FAULTY}
    "allowed_leader_type": "FAULTY",
    "n_rounds": 4,
    # Whether to generate test cases sequentially or randomized.
    "is_deterministic": True,
    # Whether to enumerate with replacement when permuting scenarios over n_rounds.
    # Only used when is_deterministic is False
    "is_with_replacement": False,
    "n_testcases": 50,
    "test_file_batch_size": 20,
    "n_twins": 1,
    # Subset of {Proposal, Vote, Timeout}, list of message types that can be dropped intra-partition
    # We allow a maximum of 2 message types dropped. If more than 2 are given, we take the first 2 in the list
    "intra_partition_drop_types": [],
    "generate_valid_partition": False,
    "seed": 12345
}