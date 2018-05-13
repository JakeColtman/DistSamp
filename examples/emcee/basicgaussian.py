from distsamp.api.redis import register_worker
from distsamp.worker.worker import Worker


def approximate_posterior(dataframe, cavity):
    from distsamp.distributions.distribution import gaussian_distribution_from_samples
    from distsamp.distributions.distribution import gaussian_convert_to_expectation_parameters
    from distsamp.distributions.state import State
    prior_mean, prior_variance = gaussian_convert_to_expectation_parameters(cavity["theta"].eta, cavity["theta"].llambda)

    import emcee
    import numpy as np
    from scipy.stats import norm

    n_walkers = 10
    n_dim = 1
    data = dataframe["x"].as_matrix()

    def lnprior(theta):
        return norm.logpdf(theta, prior_mean, np.power(prior_variance, 0.5))

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

    from distsamp.distributions.state import State
    from distsamp.distributions.distribution import gaussian_distribution_from_expectation_parameters
    from distsamp.model.model import set_prior
    from distsamp.api.redis import get_server_api
    from distsamp.model.local import LocalData, LocalModel

    MODEL_NAME = "SimpleTestSix"

    prior = State({"theta": gaussian_distribution_from_expectation_parameters(np.array(10.0), np.diag([100.0]))})
    set_prior(MODEL_NAME, prior)

    dataframe = make_data()

    sns.distplot(dataframe[dataframe.name == "a"].x)
    sns.distplot(dataframe[dataframe.name == "b"].x)

    plt.show()

    local_data = LocalData(dataframe, "name", 2, make_worker)

    local_data.run()

    from distsamp.api.redis import get_server_api
    from distsamp.distributions.distribution import gaussian_convert_to_expectation_parameters

    server_api = get_server_api(MODEL_NAME)
    shared_state = server_api.get_shared_state()
    eta, llambda = shared_state["theta"].eta, shared_state["theta"].llambda
    mean, variance = gaussian_convert_to_expectation_parameters(eta, llambda)
    sns.distplot(np.random.normal(mean[0][0], variance[0][0], 1000))

    plt.show()
