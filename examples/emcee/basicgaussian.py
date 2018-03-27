
import pandas as pd
import numpy as np
import seaborn as sns

from distsamp.modeells.api import get_server_api, get_sqlContext
from distsamp.worker.api import get_worker_api
from distsamp.server.api import get_model_api


def make_data():

    x_1 = np.random.normal(0, 1, 100)
    x_2 = np.random.normal(2, 1, 100)

    df_1 = pd.DataFrame({"x": x_1})
    df_1["name"] = "a"

    df_2 = pd.DataFrame({"x": x_2})
    df_2["name"] = "b"

    return pd.concat([df_1, df_2])

data = make_data()

sns.distplot(data[data.name == "a"].x)
sns.distplot(data[data.name == "b"].x)
sns.distplot(data.x)

sqlContext = get_sqlContext()
sdf = sqlContext.createDataFrame(data).repartition(2, "name")


def run_worker(data):
    import numpy as np
    from scipy.stats import norm

    def run_model(data, cavity):
        import emcee

        n_walkers = 10
        n_dim = 1

        def lnprior(theta):
            return norm.logpdf(theta, cavity["theta"]["mean"], np.power(cavity["theta"]["variance"], 0.5))

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
        state = {"theta": {"mean": sample_mean, "variance": sample_variance}}
        return state

    from distsamp.worker.api import register_worker
    from distsamp.worker.epworker import EPWorker

    data = [float(r["x"]) for r in data]

    w_api = register_worker("big_gaussian")
    worker = EPWorker(w_api, run_model)
    for x in worker.run(data):
        yield x