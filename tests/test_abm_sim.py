from PSSimPy.simulator import ABMSim
from PSSimPy.utils import minutes_between

sim = ABMSim('08:00', '17:00')
sim.run()