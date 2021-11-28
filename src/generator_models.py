import json


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
    batch_size:int
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
    num_non_empty_partition : int
    leader_type : str

class JsonObject:
    def __init__(self, n_validators, n_twins, n_rounds, partition_size, twin_ids, drop_configs,
                 round_leader_partitions):
        self.n_validators = n_validators
        self.n_twins = n_twins
        self.n_rounds = n_rounds
        self.partition_size = partition_size
        self.twin_ids = twin_ids
        self.round_leader_partitions = round_leader_partitions
        # todo add drop config later
        self.drop_configs = None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)

    @staticmethod
    def object_decoder(json_obj):
        return JsonObject(
            json_obj['n_validators'], json_obj['n_twins'], json_obj['n_rounds'], json_obj['partition_size'],
            json_obj['twin_ids'], json_obj['drop_configs'], json_obj['round_leader_partitions']
        )
