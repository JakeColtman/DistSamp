.. DistSamp documentation master file, created by
   sphinx-quickstart on Sun May 20 09:50:14 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

DistSamp
========

DistSamp is a library for running Bayesian analysis at scale.  It allows us to use methods like MCMC and VI on data sets which are too large to either fit in memory or be computed in reasonable time.

How it works:
-------------

DistSamp works by approximating the full posterior with a factorization.  The posterior is broken into the product of a prior and a set of sites.  Each site is approximated independently, using the the remaining components of the factorization as a prior.



Contents:

.. toctree::
   :maxdepth: 2

   Quickstart
   Model
   Server
   Site
   Data