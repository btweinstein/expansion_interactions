import numpy as np

# Set parameters...just using default from my experiments
Dw = 0.092
u = 1.15
Ro_star = 3.50
Ro = 1.84
Dg = .56

# For superdiffusive walk
Db = 0.13
b = 1.53

# Critical fitness that determines if things are noisy or not
sc = Dw/Dg**2

class Strain(object):
    def __init__(self, name, growth_rate):
        self.name = name
        self.growth_rate = growth_rate

class Strain_Interaction(object):
    """Defines all properties via the combination of both strains."""
    def __init__(self, strain_1, strain_2, wave_type):
        self.strain_1 = strain_1
        self.strain_2 = strain_2

        g1 = strain_1.growth_rate
        g2 = strain_2.growth_rate
        self.s = 2.*(g1 - g2)/(g1 + g2)

        if np.abs(self.s) < sc:
            if self.s > 0:
                print self.strain_1.name, self.strain_2.name, self.s, 'has a noisy selection coefficient!'
        else:
            if self.s > 0:
                print self.strain_1.name, self.strain_2.name, self.s, 'has a deterministic selection coefficient!'

        self.vw = None
        if wave_type is 'deterministic':
            self.vw = 2 * np.sqrt(self.s*Dw)
        if wave_type is 'noisy':
            self.vw = 2*self.s*Dw/Dg

        # Derive kappa
        self.kappa = self.vw*np.sqrt(Ro/(u*Dw))

        # Derive Ls
        self.Ls = u*Dw/self.vw**2

class Derive_From_Weakest_Strain(object):

    def __init__(self, strain_names, vw, wave_type):
        """Assumes that velocities are relative to strain 0!"""
        self.strain_names = strain_names
        self.vw_measured = vw

        self.num_strains = len(vw)

        self.wave_type = wave_type

        # Derive relative growth rates relative to the first strain

        print 'sc is:' , sc

        g = np.zeros(self.num_strains, dtype=np.double)
        g[0] = 1
        for i in range(1, self.num_strains):
            zeta = None
            if wave_type is 'deterministic':
                zeta = self.vw_measured[i]**2/(4*Dw)
            if wave_type is 'noisy':
                zeta = self.vw_measured[i]*Dg/(2*Dw)

            g[i] = (2 + zeta)/(2-zeta)

        # Based on the relative growth rates, create strains and then all possible interactions.
        # Luckily, only relative rates matter!

        self.strains = []
        for i in range(self.num_strains):
            new_strain = Strain(self.strain_names[i], g[i])
            self.strains.append(new_strain)

        # Based on the existing strains, create all interactions
        self.strain_interactions = []
        for i in range(self.num_strains):
            for j in range(self.num_strains):
                if i != j: # Ignore interactions of one strain at a time
                    new_interaction = Strain_Interaction(self.strains[i], self.strains[j], self.wave_type)
                    self.strain_interactions.append(new_interaction)
