class NetworkPlayground:
    # Sets up the
    def setup(self, test_case):
        self.test_case = test_case
        # HashMap that keeps track of all the rounds that have been reached by the validators
        self.validators_at_round = dict()


    # Receive handler. Waits for message from validators and simulates the partition logic
    def receive(
            self,
            ('ValidatorMessage', to_twin_validator_id, from_twin_validator_id,
             message, message_type, self.twin_id, round_num),
            from_=from_validator_id):

        if round_num > self.test_case.n_rounds:
            # if the round number exceeds the testcase rounds, we will forward the message reliably,
            # without considering any network partitions
            send((message_type, message), to=to_twin_validator_id)
            return

        # Get the leader_partition for the round number
        leader_partition = self.test_case.leader_partitions[round_num]

        # If the sender and receiver are in the same partition, and the message is not
        # dropped within the partition, then send the message
        for partition in leader_partition.partitions:
            if from_twin_validator_id in partition and to_twin_validator_id in partition \
                    and message_type not in leader_partition.dropped_messages:
                send((message_type, message), to=to_twin_validator_id)

        # Generates a list of honest validators(validators that do not have a twin)
        honest_validators = []
        for validator_id in range(1, self.test_case.n_validators + 1):
            if validator_id not in self.test_case.twin_ids:
                honest_validators.append(validator_id)


        if round_num not in self.validators_at_round:
            self.validators_at_round[round_num] = set()

        # we update the validators_at_round hash map to keep track of the latest round that each of
        # the validators have reached
        self.validators_at_round[round_num].add(from_validator_id)

        # As we are executing n_rounds + 3 rounds, if all honest validators have reached that round,
        # we need to terminate this test case.
        if self.test_case.n_rounds + 3 in self.validators_at_round:
            send_terminate = True
            for validator_id in honest_validators:
                if validator_id not in self.validators_at_round[self.test_case.n_rounds + 3]:
                send_terminate = False
                break

            if send_terminate is True:
                send(('Terminate'), to=test_executor)
