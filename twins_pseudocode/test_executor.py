from twins.validator import TwinsValidator


class TestExecutor:
    def execute(self, test_configs):
        for test_config in test_configs:
            # Pass the config to test_generator and generate the test case
            test_case = self.test_generator.generate_test_case(test_config)

            # Spawn the network playground with the generated test case
            network_playground = new(NetworkPlayground, num=1)
            setup(network_playground, test_case)
            run(network_playground)

            validator_ids = range(1, test_config.n_rounds+1)

            # Pick a non-faulty validator to be the default leader after n_rounds are executed
            for validator_id in validator_ids:
                if validator_id not in test_case.twin_ids:
                    default_leader = validator_id
                    break

            # Get the list of leaders to setup validators leader_election
            leaders = [leader_partition.leader for leader_partition in test_case.leader_partitions]

            # Generate public-private key pairs for each validator. crypto.generate_key_pairs
            # returns a dictionary mapping validator_id to the public_private key pair
            public_private_keys = crypto.generate_key_pairs(test_config.n_validators)
            public_keys = [public_private_keys[validator_id].public_key for validator_id in validator_ids]

            # Setting up validators and twins
            for validator_id in validator_ids:
                private_key = public_private_keys[validator_id].private_key

                # Spawn the normal validator
                validator = new(TwinsValidator, num=1)
                setup(
                    validator,
                    (validator_id, validator_ids, f, private_key, public_keys, delta,
                        test_config.n_rounds,
                        # The twin_id for normal validators is same as the validator_id
                        str(validator_id),
                        leaders, default_leader
                    )
                )
                run(validator)

                # Spawn the twin validator
                if validator_id in test_case.twin_ids:
                    twin_validator = new(TwinsValidator, num=1)
                    setup(
                        twin_validator,
                        (validator_id, validator_ids, f, private_key, public_keys, delta,
                            test_config.n_rounds,
                            # For twins, we append a _twin for the twin_id
                            str(validator_id) + "_twin",
                            leaders, default_leader
                        )
                    )
                    run(twin_validator)

            # Wait for network playground to indicate that the test case is terminated
            await(('Terminate'), from_=network_playground)

            # Perform safety and liveness checks
            safety_check = twins_validation.safety_check(validator_ids, test_case.twin_ids)
            liveness_check = twins_validation.liveness_check(validator_ids, test_case.twin_ids)

            # Generate test report
            reporting.generate_test_report(test_config, test_case, safety_check, liveness_check)
