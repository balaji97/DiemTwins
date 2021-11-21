from src.cryptography import Cryptography

def generate_key_pairs(n_validators: int):
    public_private_keys = {}
    cgraphy = Cryptography()
    validator_ids = range(1, n_validators + 1)
    for validator_id in validator_ids:
        key_pair = cgraphy.generate_key()
        public_private_keys[validator_id]["private_key"] = key_pair[0]
        public_private_keys[validator_id]["public_key"] = key_pair[1]

    return public_private_keys