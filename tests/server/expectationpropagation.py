import unittest

from distsamp.server.server import Server
from distsamp.distributions.distribution import convert_to_natural_parameters, convert_to_expectation_parameters


class ExpectationPropagationServerTest(unittest.TestCase):

    def test_natural_parameter_calculation_reversible(self):
        mean, variance = 10.0, 20.0
        eta, llambda = convert_to_natural_parameters(mean, variance)
        mean_, variance_ = convert_to_expectation_parameters(eta, llambda)
        self.assertEqual(mean, mean_)
        self.assertEqual(variance, variance)

    def test_simple_case(self):

        prior = {"alpha": {"mean": 10.0, "variance": 1.0}}
        observation = {"alpha": {"mean": 8.0, "variance": 1.0}}
        true_updated_mean = 9.0
        true_updated_variance = 0.5

        site_states = {0: prior, 1: observation}

        runner = Server.updated_shared_state(site_states)

        self.assertEqual(true_updated_mean, runner["alpha"]["mean"])
        self.assertEqual(true_updated_variance, runner["alpha"]["variance"])


if __name__ == '__main__':
    unittest.main()
