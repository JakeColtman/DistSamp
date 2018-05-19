from distsamp.api.redis import get_server_api


def plot_shared_state_through_time(model_name, variable):
    import seaborn as sns
    from matplotlib import pyplot as plt
    server_api = get_server_api(model_name)
    offset = -2
    while True:
        shared_state = server_api.get_shared_state(offset)
        if shared_state is None:
            break
        sns.distplot(shared_state[variable].to_scipy().rvs(1000), label=str(offset * -1))
        offset -= 1
    plt.legend()
    plt.title("Convergence of `{}` through iterations".format(variable))
