import json

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
