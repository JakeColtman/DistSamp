import unittest

import numpy as np

from distsamp.distributions.distribution import convert_to_expectation_parameters, convert_to_natural_parameters


class DistributionConversionTest(unittest.TestCase):

    def test_conversion_reversible(self):
        true_mu, true_variance = 2.0, 10.0
        eta, llambda = convert_to_natural_parameters(np.array(true_mu), np.array(true_variance))
        back_mu, back_variance = convert_to_expectation_parameters(eta, llambda)

        self.assertEqual(true_mu, back_mu)
        self.assertEqual(true_variance, back_variance)

    def test_simple_known_case(self):
        eta, llambda = convert_to_natural_parameters(np.array([5]), np.diag([10]))
        self.assertEqual(eta, 0.5)
        self.assertEqual(llambda, 0.1)

    def test_simple_known_multivariate(self):
        true_mu = np.array([5.0, 10.0])
        true_var = np.diag([1, 2])
        eta, llambda = convert_to_natural_parameters(true_mu, true_var)

        self.assertListEqual(list(eta.flatten()), [5, 5])
        self.assertListEqual(list(llambda.flatten()), [1.0, 0, 0, 0.5])

    def test_multivariate_conversion_reversible(self):
        true_mu = np.array([5.0, 10.0])
        true_var = np.diag([1, 2])
        eta, llambda = convert_to_natural_parameters(true_mu, true_var)
        back_mu, back_var = convert_to_expectation_parameters(eta, llambda)

        self.assertListEqual(list(true_mu.flatten()), list(back_mu.flatten()))
        self.assertListEqual(list(true_var.flatten()), list(back_var.flatten()))


if __name__ == "__main__":
    unittest.main()