# We will ensure safety property in offline mode.
# For all non-faulty validators, check if all the transactions are committed in the same order.
def safety_check(validator_ids, twin_ids):
    # First we generate list of honest validators
    honest_validators = []
    for validator_id in validator_ids:
        if validator_id not in twin_ids:
            honest_validators.append(validator_id)

    # For each pair of honest validators, we check if their ledgers match
    for first_validator_id in honest_validators:
        for second_validator_id in honest_validators:
            if not verify_ledger_files(
                    read_ledger_file(first_validator_id),
                    read_ledger_file(second_validator_id)
            ):
                return False

    return True


def verify_ledger_files(ledger_file_1, ledger_file_2):
    # Compare transactions in ledger line-by line and see if they match
    for ledger_entry_1, ledger_entry_2 in zip(ledger_file_1, ledger_file_2):
        if ledger_entry_1 != ledger_entry_2:
            return False
    return True


# At the end of n_rounds, the new leader proposes a block with payload as 'Last_transaction',
# and we do not create any network partitions.
# If this block commits, then we have passed the liveness check
def liveness_check(validator_ids, twin_ids):
    for validator in validator_ids:
        if validator not in twin_ids:
            ledger_file_validator = read_ledger_file(validator)
            # Checks the last committed transaction in all honest validators
            if ledger_file_validator[-1] != "Last_transaction":
                return False
            else:
                return True


# Returns a list of all transactions committed in a validator's ledger
def read_ledger_file(validator_id):
    # Assume that ledger is named like ledger_1.txt etc
    validator_ledger_filename = 'ledger_' + validator_id + '.txt'
    file = open(validator_ledger_filename, 'r')

    # returns all lines in ledger file as a list
    return file.readlines()