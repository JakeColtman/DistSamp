from distsamp.state.state import State


def make_data():
    # Choose the "true" parameters.
    m_true = -10

    # Generate some synthetic data from the model.
    N = 50
    N_a, N_b = N // 2, N - (N // 2)
    x = np.sort(10 * np.random.rand(N))
    y = m_true * x + np.random.normal(0, 5, N)

    return pd.DataFrame({"X": x, "y": y, "name": ["a"] * N_a + ["b"] * N_b})


def approximate_posterior(dataframe, prior: State) -> State:
    from distsamp.distributions import GaussianDistribution, GammaDistribution
    from distsamp.state.state import State

    import emcee
    import numpy as np
    from scipy.stats import norm

    n_walkers = 10
    n_dim = 2
    X = dataframe["X"]
    y = dataframe["y"]

    def lnprior(theta):
        b, s = theta
        if s <= 0:
            return - np.inf
        return prior["beta"].to_scipy().logpdf(b) + prior["sigma"].to_scipy().logpdf(s)

    def lnlike(theta, X, y):
        b, s = theta
        eta = b * X
        return np.sum(norm.logpdf(y, eta, s))

    def lnprob(theta, X, y):
        prior_prob = lnprior(theta)
        if not np.isfinite(prior_prob):
            return - np.inf
        return lnlike(theta, X, y) + prior_prob

    start_point = [[6., 3.] + np.random.normal(0, 0.001, n_dim) for _ in range(n_walkers)]

    sampler = emcee.EnsembleSampler(n_walkers, n_dim, lnprob, args=(X, y))

    pos, _, _ = sampler.run_mcmc(start_point, 500)
    sampler.reset()
    pos, _, _ = sampler.run_mcmc(pos, 500)
    return State({
        "beta": GaussianDistribution.from_samples(sampler.flatchain[:, 0]),
        "sigma": GammaDistribution.from_samples(sampler.flatchain[:, 1]),

    })


if __name__ == "__main__":
    import pandas as pd
    import numpy as np
    from matplotlib import pyplot as plt

    from distsamp.state.state import State
    from distsamp.distributions import GammaDistribution, GaussianDistribution
    from distsamp.api.redis import get_server_api
    from distsamp.model.local import SerialLocalModel
    from distsamp.site.site import sites_from_local_dataframe

    dataframe = make_data()
    plt.scatter(dataframe["X"], dataframe["y"])
    plt.show()

    MODEL_NAME = "SimpleOLS"
    prior = State({
        "beta": GaussianDistribution.from_expectation_parameters(10.0, 100.0),
        "sigma": GammaDistribution.from_expectation_parameters(1., 2.)
    })

    sites = sites_from_local_dataframe(MODEL_NAME, dataframe, "name", approximate_posterior, damping=0.2)

    local_model = SerialLocalModel(MODEL_NAME, prior, sites)
    local_model.run_iterations(5)

    server_api = get_server_api(MODEL_NAME)
    shared_state = server_api.get_shared_state()

    plt.scatter(dataframe["X"], dataframe["y"])
    beta_mean = shared_state["beta"].to_scipy().mean()
    plt.plot([0, 10], [0, beta_mean * 10])

    beta_sample = shared_state["beta"].to_scipy().rvs(1)
    sigma_sample = shared_state["sigma"].to_scipy().rvs(1)
    plt.scatter(dataframe["X"], beta_sample * dataframe["X"] + np.random.normal(0, sigma_sample, size=len(dataframe)))

    plt.show()

