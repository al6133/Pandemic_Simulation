import matplotlib.pyplot as plt
from base import ROOT_DIR
plots_folder = ROOT_DIR / "pandemic_flu_spread/plots"


def plot_sim(df, probability_infection, days_to_recover, plot_name):

    susceptible = df.iloc[:, 0]
    infected = df.iloc[:, 1]
    recovered = df.iloc[:, 2]
    days = list(df.index.values)

    fig = plt.figure(facecolor='w', figsize=(12, 7))
    ax = fig.add_subplot(111, facecolor='#dddddd', axisbelow=True)
    ax.plot(days, susceptible, 'b',
            alpha=0.5, linestyle = '--', lw=2, label='Susceptible')
    ax.plot(days, infected, 'r',
            alpha=0.5, linestyle = '--', lw=2, label='Infected')
    ax.plot(days, recovered, 'g',
            alpha=0.5, linestyle = '--', lw=2, label='Recovered with immunity')

    ax.set_xlabel('Days')
    ax.set_ylabel('Number of Students')
    plt.title(f"Population distribution with probability_infection = "
              f"{probability_infection} & recovery time of {days_to_recover} days")

    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)

    ax.grid(b=False, which='both', c='w', lw=2, ls='-')
    legend = ax.legend()
    legend.get_frame().set_alpha(0.5)
    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)
    plt.savefig(plots_folder / (plot_name + ".svg"))
    plt.show()
