class LeaderElection:

    def __init__(self, leaders, default_leader):
        self.leaders = leaders
        self.default_leader = default_leader

    def get_leader(self, round_num):
        # As leaders are 0-indexed and rounds start at 1
        return self.leaders[round_num - 1] if round_num - 1 < len(self.leaders) else self.default_leader
