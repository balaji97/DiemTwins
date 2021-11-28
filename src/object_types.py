from typing import List

from cryptography import Cryptography

'''
VoteInfo
    id, round; // Id and round of block
    parent id, parent round; // Id and round of parent
    exec state id; // Speculated execution state
'''


class VoteInfo:
    def __init__(self, id=None, round=None, parent_id=None, parent_round=None, exec_state_id=None):
        self.id = id
        self.round = round  # Id and round of block
        self.parent_id = parent_id
        self.parent_round = parent_round  # Id and round of parent
        self.exec_state_id = exec_state_id  # Speculated execution state


'''
// speculated new committed state to vote directly on
LedgerCommitInfo
    commit state id; // ⊥ if no commit happens when this vote is aggregated to QC
    vote info hash; // Hash of VoteMsg.vote info
'''


class LedgerCommitInfo:
    def __init__(self, commit_state_id=None, vote_info_hash=None):
        # ⊥ if no commit happens when this vote is aggregated to QC
        self.commit_state_id = commit_state_id
        self.vote_info_hash = vote_info_hash  # Hash of VoteMsg.vote info


'''
VoteMsg
    vote info; // A VoteInfo record
    ledger commit info; // Speculated ledger info
    high commit qc; // QC to synchronize on committed blocks
    sender ← u; // Added automatically when constructed
    signature ← signu(ledger commit info); // Signed automatically when constructed
'''


class VoteMsg:
    def __init__(self, vote_info=None, ledger_commit_info=None, high_commit_qc=None, validator_id=0):
        self.vote_info = vote_info  # A VoteInfo record
        self.ledger_commit_info = ledger_commit_info  # Speculated ledger info
        self.high_commit_qc = high_commit_qc  # QC to synchronize on committed blocks
        self.sender = validator_id  # Added automatically when constructed
        # self.signature = self.ledger_commit_info
        self.signature = Cryptography.sign_message(Cryptography.hash(self.ledger_commit_info))


'''
// QC is a VoteMsg with multiple signatures
QC
    vote info;
    ledger commit info;
    signatures; // A quorum of signatures
    author ← u; // The validator that produced the qc
    author signature ← signu(signatures);
'''


class QC:
    def __init__(self, vote_info=None, ledger_commit_info=None, signatures=None, author=None, signers=None):
        self.vote_info = vote_info
        self.ledger_commit_info = ledger_commit_info
        self.signatures = signatures  # A quorum of signatures
        self.author = author  # The validator that produced the qc
        self.signers = signers
        self.author_signature = Cryptography.sign_message(self.signatures)


'''
Block
    author; // The author of the block, may not be the same as qc.author after view-change
    round; // Yhe round that generated this proposal
    payload ; // Proposed transaction(s)
    qc ; // QC for parent block
    id; // A unique digest of author, round, payload, qc.vote info.id and qc.signatures
'''


class Block:
    def __init__(self, author=None, round=None, payload=None, qc=None, id=None):
        # The author of the block, may not be the same as qc.author after view-change
        self.author = author
        self.round = round  # The round that generated this proposal
        self.payload = payload  # Proposed transaction(s)
        self.qc = qc  # QC for parent block
        self.id = id  # A unique digest of author, round, payload, qc.vote info.id and qc.signatures
        self.author_signature = Cryptography.sign_message(self.payload)


'''
TimeoutInfo
    round;
    high qc;
    sender ← u; // Added automatically when constructed
    signature ← signu(round, high qc.round); // Signed automatically when constructed
'''


class TimeoutInfo:
    def __init__(self, round=None, high_qc=None, validator_id=0):
        self.round = round
        self.high_qc = high_qc
        self.author = validator_id  # Added automatically when constructed
        # Signed automatically when constructed
        # self.signature = round + self.high_qc.round
        if high_qc is None:
            high_qc_round = None
        else:
            high_qc_round = high_qc.vote_info.round
        self.author_signature = Cryptography.sign_message(
            Cryptography.hash(str(round)+","+str(high_qc_round)))


'''
TC
    round; // All timeout messages that form TC have the same round
    tmo high qc rounds; // A vector of 2f + 1 high qc round numbers of timeout messages that form TC
    tmo signatures; // A vector of 2f + 1 validator signatures on (round, respective high qc round)
'''


class TC:
    def __init__(self, round=None, tmo_high_qc_rounds=None, signatures=None, signers=None, author=None):
        self.round = round  # All timeout messages that form TC have the same round
        # A vector of 2f + 1 high qc round numbers of timeout messages that form TC
        self.tmo_high_qc_rounds = tmo_high_qc_rounds
        # A vector of 2f + 1 validator signatures on (round, respective high qc round)
        self.tmo_signatures = signatures
        self.tmo_signers = signers
        self.author = author
        self.author_signature = Cryptography.sign_message(self.tmo_signatures)


'''
TimeoutMsg
    tmo info; // TimeoutInfo for some round with a high qc
    last round tc; // TC for tmo info.round − 1 if tmo info.high qc.round 6= tmo info.round − 1, else ⊥
    high commit qc; // QC to synchronize on committed blocks
'''


class TimeoutMsg:
    def __init__(self, tmo_info=None, last_round_tc=None, high_commit_qc=None):
        self.tmo_info = tmo_info  # TimeoutInfo for some round with a high qc
        # TC for tmo info.round − 1 if tmo info.high qc.round 6= tmo info.round − 1, else ⊥
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc  # QC to synchronize on committed blocks


'''
ProposalMsg
    block;
    last round tc; // TC for block.round − 1 if block.qc.vote info.round 6= block.round − 1, else ⊥
    high commit qc; // QC to synchronize on committed blocks
    signature ← signu(block.id);
'''


class ProposalMsg:
    def __init__(self, block=None, last_round_tc=None, high_commit_qc=None, validator_id=0):
        self.block = block
        # TC for block.round − 1 if block.qc.vote info.round 6= block.round − 1, else ⊥
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc  # QC to synchronize on committed blocks
        self.sender = validator_id
        self.signature = Cryptography.sign_message(Cryptography.hash(self.block.id))


class Partition:
    dropped_messages: list
    partitions: list

    def __init__(self, partition):
        # todo populate dropped messages
        self.dropped_messages = []
        self.partitions = partition

class LeaderPartition:
    leader: int
    partitions: List[Partition]

    def __init__(self, round_leader_partition: list):
        self.leader = int(round_leader_partition[0])
        self.partitions = [Partition(partition) for partition in round_leader_partition[1]]


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
    test_id: int
    safety_check: bool
    liveness_check: bool
    elapsed_time: int

    def __init__(self, test_id, safety_check, liveness_check, elapsed_time):
        self.test_id = test_id
        self.safety_check = safety_check
        self.liveness_check = liveness_check
        self.elapsed_time = elapsed_time

    def __str__(self):
        return  "{ " + ", ".join([
            "test_id: " + str(self.test_id),
            "safety_check: " + str(self.safety_check),
            "liveness_check: " + str(self.liveness_check),
            "elapsed_time: " + str(self.elapsed_time)
        ]) + " }"
