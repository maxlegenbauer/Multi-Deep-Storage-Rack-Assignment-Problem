import pandas as pd
from gurobipy import Model, GRB, quicksum

class MultiDeepStorageModel:
    def __init__(self, J, bar_J, S, D, Rho_j, R):

        self.model = Model("Multi-Deep Storage")
        self.J = J 
        self.bar_J = bar_J 
        self.S = S  
        self.D = D 
        self.R = R
        self.Rho_j = Rho_j  
        self.S_s = {}
        self._initialize_S_s()

        self.S_j = {}
        self._initialize_S_j()

        self.Theta_s = {}  
        self.theta_ss_prime_1 = {}  
        self.theta_ss_prime_2 = {}  
        self._initialize_theta()
        
        self.x = None
        self.b_1 = None
        self.b_2 = None
        self._initialize_variables()
        self._set_objective()
        self._add_constraints()

    def _initialize_S_s(self):
        self.S_s = {}  
        for s in self.S:
            self.S_s[s] = [
                s_prime for s_prime in self.S
                if s[0] == s_prime[0] and s[1] == s_prime[1] and 
                ((s[2] > s_prime[2] and s_prime[2] > 0) or (s[2] < s_prime[2] and s_prime[2] < 0))
            ]

    def _initialize_S_j(self):
        for j in self.J:
            self.S_j[j] = [
                s for s in self.S if self.break_interval(j, s)[0] < self.break_interval(j, s)[1]
            ]
            if not self.S_j[j]:
                raise ValueError(f"S_j for stopover {j} is empty. No valid storage positions were found.")

    def _initialize_theta(self):
        for s in self.S:
            self.Theta_s[s] = [
                (j1, j2) for j1 in self.J for j2 in self.J if j1 != j2 and self.is_sharing_break_interval(j1, j2, s)
            ]

        for s in self.S:
            for s_prime in self.S_s[s]:
                self.theta_ss_prime_1[(s, s_prime)] = [
                    (j1, j2) for j1 in self.J+self.bar_J for j2 in self.J+self.bar_J if j1 != j2 and self.is_blocked_at_storing(j1, j2, s, s_prime)
                ]

        for s in self.S:
            for s_prime in self.S_s[s]:
                self.theta_ss_prime_2[(s, s_prime)] = [
                    (j1, j2) for j1 in self.J+self.bar_J for j2 in self.J+self.bar_J if j1 != j2 and self.is_blocked_at_retrieval(j1, j2, s, s_prime)
                ]

    def _initialize_variables(self):
        self.x = self.model.addVars(
            ((j, s) for j in self.J + self.bar_J for s in self.S),
            vtype=GRB.BINARY,
            name="x"
        )
        
        self.b_1 = self.model.addVars(
            ((s, s_prime, j) for s in self.S for s_prime in self.S_s[s] for j in self.J+self.bar_J),
            vtype=GRB.BINARY,
            name="b_1"
        )
        self.b_2 = self.model.addVars(
            ((s, s_prime, j) for s in self.S for s_prime in self.S_s[s] for j in self.J+self.bar_J),
            vtype=GRB.BINARY,
            name="b_2"
        )

    def _set_objective(self):
        self.model.setObjective(
            quicksum(self.get_E()[j, s] * self.x[j, s] for j in self.J for s in self.S) +
            quicksum((self.b_1[s, s_prime, j] + self.b_2[s, s_prime, j]) * 4 * abs(s[2])
                     for j in self.J + self.bar_J for s in self.S for s_prime in self.S_s[s]),
            GRB.MINIMIZE
        )

    def _add_constraints(self):
        self.model.addConstrs(
            (quicksum(self.x[j, s] for s in self.S_j[j]) == 1 for j in self.J),
            name="one_storage_per_stopover"
        )

        self.model.addConstrs(
            (self.x[j1, s] + self.x[j2, s] <= 1 for s in self.S for j1, j2 in self.Theta_s[s]),
            name="no_overlap_at_position"
        )

        self.model.addConstrs(
            (self.b_1[s, s_prime, j] >= self.x[j, s] + self.x[j_prime, s_prime] - 1
             for s in self.S for s_prime in self.S_s[s] for j, j_prime in self.theta_ss_prime_1[(s, s_prime)]),
            name="blockage_conditions1"
        )
        self.model.addConstrs(
            (self.b_2[s, s_prime, j] >= self.x[j, s] + self.x[j_prime, s_prime] - 1
             for s in self.S for s_prime in self.S_s[s] for j, j_prime in self.theta_ss_prime_2[(s, s_prime)]),
            name="blockage_conditions2"
        )

        self.model.addConstrs(
            (self.x[j, s] == 1 for j in self.bar_J for s in [self.Rho_j[j]]),
            name="virtual_stopovers"
        )
    
    def optimize(self):
        self.model.optimize()

    def to_string(self):
        if self.model.status == GRB.OPTIMAL:
            print("====================================================================")
            print("Optimale Lösung gefunden:")
            print("====================================================================\n")
            print("                            Initinal Stopovers                      \n")
            for j in self.bar_J:
                for s in [self.Rho_j[j]]:
                    if self.x[j, s].x > 0.5:
                        print(f"Initial Stopover {j} wird Position {s} zugewiesen.")
            print("____________________________________________________________________\n")
            print("                          Interim Stopovers                         \n")
            for j in self.J:
                for s in self.S:
                    if self.x[j, s].x > 0.5:
                        if j[2] != 'p_dummy':
                            print(f"Stopover {j} wird Position {s} zugewiesen.")
            print("____________________________________________________________________\n")
            print("                             End Stopovers                          \n")
            for j in self.J:
                for s in self.S:
                    if self.x[j, s].x > 0.5:
                        if j[2] == 'p_dummy':
                            print(f"Stopover {j} wird Position {s} zugewiesen.")
            print("____________________________________________________________________\n")
            print("                              Blockages                             \n")
            for j in self.J+self.bar_J:
                for s in self.S:
                    for s_prime in self.S_s[s]:
                        if self.b_1[s,s_prime,j].x > 0.5:
                            print(f"Für Stopover {j} für Position {s} wurde {s_prime} verschoben (Einlagern)")
                        if self.b_2[s,s_prime,j].x > 0.5:
                            print(f"Für Stopover {j} für Position {s} wurde {s_prime} verschoben (Auslagern)")

            print("====================================================================\n")
            print(f"Gesamtkosten: {self.model.objVal}")
        else:
            print("Keine optimale Lösung gefunden.")
    
    def get_E(self):
        E = {(j, s): self.D[(j[1],s)] + self.D[(j[2],s)] for j in self.J for s in self.S}
        return E

    def break_interval(self,j,s):
        def beta(s):
            return abs(s[2]) * (abs(s[2]) - 1)

        if j[3] is None:
            a_js = 0
            if j[4] - self.D[(j[2],s)] - beta(s) < 0:
                if s in [self.Rho_j[j]]:
                    raise ValueError(f"initial storage position {s} is to far away for virtual stopover {j}")
        else:
            a_js = j[3] + self.D[(j[1],s)] + beta(s)
        if j[2] == 'p_dummy':
            d_js = j[4] - self.D[(j[2],s)]
        else:
            d_js = j[4] - self.D[(j[2],s)] - beta(s)
        return (a_js,d_js)
    
    def is_sharing_break_interval(self,j1,j2,s):
        interval_j1 = self.break_interval(j1,s)
        interval_j2 = self.break_interval(j2,s)
        overlap = max(interval_j1[0], interval_j2[0]) < min(interval_j1[1], interval_j2[1])
        return overlap 
    
    def is_blocked_at_storing(self,j1,j2,s1,s2):
        (a_j1s1, d_j1s1) = self.break_interval(j1,s1)
        (a_j2s2, d_j2s2) = self.break_interval(j2,s2)
        return a_j1s1 < d_j2s2 and a_j1s1 > a_j2s2
    
    def is_blocked_at_retrieval(self,j1,j2,s1,s2):
        (a_j1s1, d_j1s1) = self.break_interval(j1,s1)
        (a_j2s2, d_j2s2) = self.break_interval(j2,s2)
        return d_j1s1 < d_j2s2 and d_j1s1 > a_j2s2

    def stopover_to_string(self,j, s):
        if j[1] is not None:
            str1 = f"{j[1]} ({j[3]}) -> [{self.D[(j[1], s)]}] -> {s} [{self.break_interval(j,s)}]" #-> [{self.D[(j[2], s)]}] -> {j[2]} ({j[4]})
        else:
            str1 = f"start at {s}"
        if j[2] == 'p_dummy':
            str2 = f" -> end ({j[4]})"
        else:
            str2 = f" -> [{self.D[(j[2], s)]}] -> {j[2]} ({j[4]})"
        print(str1+str2)
    
    def storage_position_to_string(self):
        for s in self.S:
            print(f"------------{s}-------------\n")
            for j in self.J + self.bar_J:
                if self.x[j,s].x > 0:
                    print(f"{self.break_interval(j,s)} for {j[0]}")

    def show_path_per_rack(self):
        for r in self.R:
            print(f"----------------- {r} -----------------")
            J_r = [tup for tup in self.J + self.bar_J if tup[0] == r]
            J_r.sort(key = lambda x: x[4])
            for j in J_r:
                for s in self.S:
                    if self.x[j,s].x > 0.5:
                        self.stopover_to_string(j,s) 
            print("\n")
