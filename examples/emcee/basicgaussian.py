
def make_data():

    import numpy as np
    x_1 = np.random.normal(0, 1, 100)
    x_2 = np.random.normal(2, 1, 100)

    df_1 = pd.DataFrame({"x": x_1})
    df_1["name"] = "a"

    df_2 = pd.DataFrame({"x": x_2})
    df_2["name"] = "b"

    return pd.concat([df_1, df_2])


def run_worker(data):

    import numpy as np
    from scipy.stats import norm

    def run_model(data, cavity):

        import emcee

        n_walkers = 10
        n_dim = 1

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

        sample_mean = np.mean(sampler.flatchain[:])
        sample_variance = np.var(sampler.flatchain[:])
        from distsamp.distributions.state import parse_state_dictionary
        state = {"theta": {"mean": sample_mean, "variance": sample_variance}}
        return parse_state_dictionary(state)

    from distsamp.worker.api.spark import register_worker
    from distsamp.worker.worker import Worker

    data = [float(r["x"]) for r in data]

    w_api = register_worker("BasicGaussian")
    worker = Worker(w_api, run_model)
    for x in worker.run(data):
        yield x


if __name__ == "__main__":
    import pandas as pd
    import numpy as np
    import seaborn as sns
    from matplotlib import pyplot as plt

    from distsamp.distributions.state import parse_state_dictionary
    from distsamp.model.api.spark import set_prior

    model_name = "BigGaussian"

    prior = parse_state_dictionary({"theta": {"mean": 10.0, "variance": 100.0}})
    set_prior(model_name, prior)

    data = make_data()

    sns.distplot(data[data.name == "a"].x)
    sns.distplot(data[data.name == "b"].x)

    plt.show()

    ### Actually run the model

    from distsamp.server.api.spark import connect_to_server
    server_api = connect_to_server(model_name)

    sns.distplot(np.random.normal(server_api.get_shared_state()["theta"].mean, 1.0, 1000))
