import emcee as em
import numpy as np


from collections import namedtuple

Job = namedtuple("Job", ["f_data", "f_model", "state"])


def hydrate_runner(job, data):
    processed_data = job.f_data(data)
    return job.f_model(processed_data, job.state)


class EmceeRunner:

    def __init__(self, f_likihood, settings, data, state):
        self.f_likihood = f_likihood
        self.state = state
        self.data = data
        self.settings = settings

    def run_epoch(self):
        ndim, nwalkers = 1, self.settings["n_walkers"]
        p0 = np.array([self.state["theta"] + np.random.normal(0, 0.01) for _ in range(nwalkers)]).reshape((nwalkers, ndim))
        sampler = em.EnsembleSampler(nwalkers, ndim, self.f_likihood, args=[self.data])
        pos, prob, state = sampler.run_mcmc(p0, self.settings["n_burn"])
        sampler.reset()
        pos, prob, state = sampler.run_mcmc(pos, self.settings["n_sample"])
        self.state["theta"] = np.mean(sampler.flatchain[:])

    def update_state(self, state):
        self.state = state

    def get_state(self):
        return self.state


if __name__ == "__main__":
    def lnprob(x, mu):
        icov = 1.0
        diff = x - mu
        return -np.dot(diff, np.dot(icov, diff)) / 2.0

    settings = {"n_walkers": 100, "n_burn": 1000, "n_sample": 1000}

    runner_factory = emcee_runner_factory(lnprob, settings)

    emcee_job = Job(lambda x: np.mean(x), runner_factory, {"theta": 10.0})

    runner = hydrate_runner(emcee_job, np.random.normal(0, 1, 10000))
    print(runner)
    # runner = EmceeRunner(lnprob, settings, np.random.normal(0, 1, 1000))
    # runner.update_state({"theta": -10.0})
    runner.run_epoch()
    print(runner.get_state())

