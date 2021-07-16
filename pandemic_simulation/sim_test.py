import pandas as pd

from pandemic_flu_spread.pandemic_classes import Student, InfectedStudent, PandemicSim
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
#%% Create initial conditions
# Susceptible students
n_s_st = 20
s_students = [Student("st_" + str(i + 1)) for i in range(n_s_st)]
# Infected students
n_i_st = 1
prob_infection = 0.02
days_to_recover = 3
i_students = [InfectedStudent("st_" + str(n_s_st + i + 1),
                              prob_infection,
                              days_to_recover)
              for i in range(n_i_st)]
# Set default values for infected students
InfectedStudent.default_prob_infection = prob_infection
InfectedStudent.default_days_to_recover = days_to_recover

trials = 2000
results = pd.DataFrame()
trial_col = "trial"
for t in range(trials):
    sim = PandemicSim(s_students, i_students)
    sim.sim_days = 30
    sim.run_sim()
    temp_results = sim.sim_log.copy()
    # temp_results[trial_col] = t + 1
    results = results.append(temp_results)

summary = results.groupby("day").mean()
summary.plot()
plt.show()
#%%
sns.boxplot(x="day", y="infected", data=results.reset_index())
plt.show()
#%% Creat pandemic simulation
sim = PandemicSim(s_students, i_students)
sim.sim_days = 30
sim.run_sim()
print(sim.sim_log)
sim.sim_log.plot()
plt.show()
