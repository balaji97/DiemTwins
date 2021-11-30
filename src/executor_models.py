from typing import List


class Partition:
    dropped_messages: list
    partitions: list

    def __init__(self, partition, dropped_messages):
        # todo populate dropped messages
        self.dropped_messages = dropped_messages
        self.partitions = partition

    def __str__(self):
        return

class LeaderPartition:
    leader: int
    partitions: List[Partition]

    def __init__(self, round_leader_partition: list):
        self.leader = int(round_leader_partition[0])

        dropped_messages = round_leader_partition[2]
        self.partitions = [Partition(partition, dropped_messages) for partition in round_leader_partition[1]]

    # def __str__(self):
    #     return "\n".join([
    #         "Leader: " + str(self.leader),
    #         "Dropped messages: " + str([partition.dropped_messages for partition in self.partitions]),
    #         "Partitions: " + str([partition.partitions for partition in self.partitions])
    #     ])

class TestCase:
    n_rounds: int
    n_validators: int
    leader_partitions: List[LeaderPartition]
    twin_ids: list
    delta: float


    def __init__(self, n_rounds: int, n_validators: int, leader_partitions: List[LeaderPartition], twin_ids: list, delta=1):
        self.n_rounds = n_rounds
        self.n_validators = n_validators
        self.leader_partitions = leader_partitions
        self.twin_ids = twin_ids
        self.delta = delta


class TestReport:
    test_file_id: int
    test_id: int
    safety_check: bool
    liveness_check: bool
    elapsed_time: int

    def __init__(self, test_file_id, test_id, safety_check, liveness_check, elapsed_time):
        self.test_file_id = test_file_id
        self.test_id = test_id
        self.safety_check = safety_check
        self.liveness_check = liveness_check
        self.elapsed_time = elapsed_time

    def __str__(self):
        return  "{ " + ", ".join([
            "test_file_id: " + str(self.test_file_id),
            "test_id: " + str(self.test_id),
            "safety_check: " + str(self.safety_check),
            "liveness_check: " + str(self.liveness_check),
            "elapsed_time: " + str(self.elapsed_time)
        ]) + " }"
