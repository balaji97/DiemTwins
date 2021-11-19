class TwinsValidator:
    def setup(
            self,
            validator_id,
            validator_ids,
            f,
            private_key,
            public_keys,
            delta,
            n_rounds,
            twin_id,
            leaders,
            default_leader
    ):
        self.twin_id = twin_id
        # initialize the leader election module with the leaders provided by twins module
        leader_election_twins.initialize(leaders, default_leader)

        # Set up validator as normal using validator_id, validator_ids,
        # f, private_key, public_keys and delta
        pass

    # Pseudocode for sending any message via network playground.
    def send(self, message, message_type, to, round_num):
        send(
            ('ValidatorMessage', to_validator_id, message, message_type, self.twin_id, round_num),
            to=network_playground
        )
