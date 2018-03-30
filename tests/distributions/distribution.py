
import unittest

import numpy as np

from distsamp.distributions.distribution import Distribution


class DistributionTest(unittest.TestCase):

    def test_serialization(self):

        distr = Distribution(1.0, 2.0, 3.0, 4.0)
        serialized = distr.to_dict()

        self.assertListEqual(list(serialized.keys()), ["mean", "variance", "eta", "llambda"])

        self.assertEqual(serialized["mean"], 1.0)

    def test_multiplication(self):
        dist_a = Distribution(np.array(1.0), np.diag([0.5]))
        dist_b = Distribution(np.array(2.0), np.diag([0.5]))

        dist_c = dist_a * dist_b

        self.assertEqual(np.array(1.5), dist_c.mean)

    def test_multiplication_reversible(self):
        dist_a = Distribution(np.array(1.0), np.diag([0.5]))
        dist_b = Distribution(np.array(2.0), np.diag([0.5]))

        dist_c = dist_a * dist_b

        dist_a_back = dist_c / dist_b

        self.assertEqual(dist_a.mean, dist_a_back.mean)
        self.assertEqual(dist_a.variance, dist_a_back.variance)


if __name__ == "__main__":
    unittest.main()
