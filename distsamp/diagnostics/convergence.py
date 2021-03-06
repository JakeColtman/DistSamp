from distsamp.api.redis import get_server_api


def plot_shared_state_through_time(model_name, variable, column=None):
    import seaborn as sns
    from matplotlib import pyplot as plt
    server_api = get_server_api(model_name)
    offset = -2
    while True:
        shared_state = server_api.get_shared_state(offset)
        if shared_state is None:
            break
        if column is None:
            sns.distplot(shared_state[variable].to_scipy().rvs(1000), label=str(offset * -1))
        else:
            sns.distplot(shared_state[variable].to_scipy().rvs(1000)[:, column], label=str(offset * -1))
        offset -= 1
    plt.legend()
    plt.title("Convergence of `{}` through iterations".format(variable))


def plot_site_state_through_time(model_name, site_id, variable, column=None):
    import seaborn as sns
    from matplotlib import pyplot as plt

    from distsamp.api.redis import get_site_api

    site_api = get_site_api(model_name, site_id)
    offset = -1
    while True:
        shared_state = site_api.get_site_state(offset)
        if shared_state is None:
            break
        if column is None:
            sns.distplot(shared_state[variable].to_scipy().rvs(1000), label=str(offset * -1))
        else:
            sns.distplot(shared_state[variable].to_scipy().rvs(1000)[:,column], label=str(offset * -1))
        offset -= 1
    plt.legend()
    plt.title("Convergence of `{}` through iterations".format(variable))
