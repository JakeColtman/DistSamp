from distsamp.api.redis import register_worker
from distsamp.worker.worker import Worker


def approximate_posterior(dataframe, cavity):
    from distsamp.distributions.distribution import gaussian_distribution_from_samples
    from distsamp.state.state import State

    import emcee
    import numpy as np
    from scipy.stats import norm

    n_walkers = 10
    n_dim = 1
    data = dataframe["x"].as_matrix()

    def lnprior(theta):
        return norm.logpdf(theta, cavity["theta"].mean, np.power(cavity["theta"].variance, 0.5))

    def lnlike(theta, data):
        return np.sum(norm.logpdf(data, theta, 1.0))

    def lnprob(theta, data):
        return lnprior(theta) + lnlike(theta, data)

    start_point = [[np.mean(data)] + np.random.normal(0, 0.001, n_dim) for _ in range(n_walkers)]

    sampler = emcee.EnsembleSampler(n_walkers, n_dim, lnprob, args=[[data]])

    pos, _, _ = sampler.run_mcmc(start_point, 500)
    sampler.reset()
    pos, _, _ = sampler.run_mcmc(pos, 500)
    theta_distribution = gaussian_distribution_from_samples(sampler.flatchain[:])
    return State({"theta": theta_distribution})


def make_worker(dataframe):
    worker_api = register_worker(MODEL_NAME)
    return Worker(worker_api, approximate_posterior, 0.2)


def make_data():
    import numpy as np
    x_1 = np.random.normal(0, 1, 100)
    x_2 = np.random.normal(2, 1, 100)

    df_1 = pd.DataFrame({"x": x_1})
    df_1["name"] = "a"

    df_2 = pd.DataFrame({"x": x_2})
    df_2["name"] = "b"

    return pd.concat([df_1, df_2])


if __name__ == "__main__":
    import pandas as pd
    import numpy as np
    import seaborn as sns
    from matplotlib import pyplot as plt

    from distsamp.state.state import State
    from distsamp.distributions.distribution import GaussianDistribution
    from distsamp.model.model import set_prior
    from distsamp.api.redis import get_server_api
    from distsamp.model.local import LocalData, LocalModel

    MODEL_NAME = "BasicGaussian"

    prior = State({"theta": GaussianDistribution.from_expectation_parameters(10.0, 100.0)})
    set_prior(MODEL_NAME, prior)

    dataframe = make_data()

    sns.distplot(dataframe[dataframe.name == "a"].x)
    sns.distplot(dataframe[dataframe.name == "b"].x)

    plt.show()

    local_data = LocalData(dataframe, "name", 2, make_worker)

    local_model = LocalModel(MODEL_NAME, [local_data])
    local_model.run()

    server_api = get_server_api(MODEL_NAME)
    shared_state = server_api.get_shared_state()

    sns.distplot(np.random.normal(shared_state["theta"].mean, shared_state["theta"].variance, 1000))

    plt.show()
