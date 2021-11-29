import json

class JsonObject:
    def __init__(self, n_validators, n_rounds, twin_ids, drop_configs,
                 round_leader_partitions):
        self.n_validators = n_validators
        self.n_rounds = n_rounds
        self.twin_ids = twin_ids
        self.round_leader_partitions = round_leader_partitions
        # todo add drop config later
        self.drop_configs = None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)

    @staticmethod
    def object_decoder(json_obj):
        return JsonObject(
            json_obj['n_validators'], json_obj['n_rounds'], json_obj['twin_ids'], json_obj['drop_configs'],
            json_obj['round_leader_partitions']
        )
