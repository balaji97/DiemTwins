from typing import List


# leader_list : list of the leaders in each round.
# default_leader: leader for the "no-op" round after execution of n_rounds.
def initialise(leaders: List, default_leader: int):
    self.leaders = leaders
    self.default_leader = default_leader


# returns the leader for the given round_num and if the round is greater than n_rounds,
# return the default leader.
def get_leader(round_num):
    if round_num < len(self.leaders):
        return self.leaders[round_num]
    else:
        return self.default_leader
