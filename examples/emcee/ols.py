from distsamp.state.state import State


def make_data():
    # Choose the "true" parameters.
    m_true = 10
    b_true = -50
    # Generate some synthetic data from the model.
    N = 50
    N_a, N_b = N // 2, N - (N // 2)
    x = np.sort(10 * np.random.rand(N))
    y = b_true + m_true * x + np.random.normal(0, 5, N)

    return pd.DataFrame({"b": [1] * N, "X": x, "y": y, "name": ["a"] * N_a + ["b"] * N_b})


def approximate_posterior(dataframe, prior: State) -> State:
    from distsamp.distributions import GaussianDistribution, GammaDistribution
    from distsamp.state.state import State

    import emcee
    import numpy as np
    from scipy.stats import norm

    n_walkers = 10
    n_dim = 3
    covariates = ["b", "X"]
    X = dataframe[covariates]
    y = dataframe["y"]

    beta_prior = prior["beta"].to_scipy()
    sigma_prior = prior["sigma"].to_scipy()

    def lnprior(theta):
        b = theta[:-1]
        s = theta[-1]
        if s <= 0:
            return - np.inf
        return beta_prior.logpdf(b) + sigma_prior.logpdf(s)

    def lnlike(theta, X, y):
        b = theta[:-1]
        s = theta[-1]
        eta = np.dot(X, b)
        return np.sum(norm.logpdf(y, eta, s))

    def lnprob(theta, X, y):
        prior_prob = lnprior(theta)
        if not np.isfinite(prior_prob):
            return - np.inf
        return lnlike(theta, X, y) + prior_prob

    start_point = [[6., 6., 3.] + np.random.normal(0, 0.001, n_dim) for _ in range(n_walkers)]

    sampler = emcee.EnsembleSampler(n_walkers, n_dim, lnprob, args=(X, y))
    print("Starting burn")
    pos, _, _ = sampler.run_mcmc(start_point, 500)
    print("Starting sampling")
    sampler.reset()
    pos, _, _ = sampler.run_mcmc(pos, 500)
    print("DONE!")
    return State({
        "beta": MultivariateGaussianDistribution.from_samples(sampler.flatchain[:, 0:2]),
        "sigma": GammaDistribution.from_samples(sampler.flatchain[:, -1]),

    })


if __name__ == "__main__":
    import pandas as pd
    import numpy as np
    from matplotlib import pyplot as plt

    from distsamp.state.state import State
    from distsamp.distributions import GammaDistribution, MultivariateGaussianDistribution
    from distsamp.api.redis import get_server_api
    from distsamp.model.local import SerialLocalModel
    from distsamp.site.site import sites_from_local_dataframe

    dataframe = make_data()
    plt.scatter(dataframe["X"], dataframe["y"])
    plt.show()

    MODEL_NAME = "SimpleOLS"
    prior = State({
        "beta": MultivariateGaussianDistribution.from_expectation_parameters(np.array([0., 0.]), np.diag([100.0, 100.0])),
        "sigma": GammaDistribution.from_expectation_parameters(1., 2.)
    })

    sites = sites_from_local_dataframe(MODEL_NAME, dataframe, "name", approximate_posterior, damping=0.2)

    local_model = SerialLocalModel(MODEL_NAME, prior, sites)
    local_model.run_until_converged()

    server_api = get_server_api(MODEL_NAME)
    shared_state = server_api.get_shared_state()

    b, m = shared_state["beta"].to_scipy().rvs()
    s = shared_state["sigma"].to_scipy().rvs()

    X = dataframe["X"]
    y_pred = b + m * X + np.random.normal(0, s, len(X))
    plt.scatter(X, y_pred)
    plt.scatter(X, dataframe["y"])

