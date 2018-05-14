# DistSamp

DistSamp is a library for running large-scale, distributed Bayesian analysis.  It is an implementation of the Expectation Propagation algorithm presented in Gelman et al (20xx).

DistSamp enables users to run common Bayesian techniques like MCMC and VI on large data sets across a cluster of machines.  This allows us to use significantly speed up the computation, and to work with data that is too large to fit in memory.

Of course, there is no free lunch.  DistSamp aims to closely approximate the results of running the data in a single process, but the distributed approach will introduce both bias and variance.


## How it works (theory)

The core concept of DistSamp is that total likihood of a model can be approximated by a factorization into a set of `Site`s, each of which contains a subset of the data.  Together the sites partition the data, s.t. each row of data appears in exactly one `Site`.

Each `Site` can be approximated independently of the other sites and the prior, allowing us to distribute the computation required to approximate the full posterior.

For more information see Gelman et al (20xx)


## How it works (mechanically)

Models are split into two types of things:

    * `Server` which aggregates together the `Site` approximations
    * `Site`s which handle the local approximations

In general, `Servers` are extremely mechanistic and don't change much between models.  `Sites`s are where the modelling work is done.  Each `Site` is composed of some data and a function for approximating the posterior.  Generally, this function does some heavy lifting like MCMC.

DistSamp offers simple ways to convert a dataframe into `Sites`.  Theoretically, DistSamp is sufficiently decentralized to allow arbitrary models and methods for adding factors to the approximation, but it tends to be faffy to do this manually and is overkill for common use cases.

The simplest approach is to use a `Data` class.  These classes encapsualte a dataframe and can provide a simple way to generate `Site`s.


## Flexibility

For most common cases, it is sufficient to use the easy constructor methods, however, DistSamp's flexible architecture allows for much more complex use cases.  As long as each `Site` offers up a set of variables compatible with the model, there almost no constraint on how and when `Sites` can be added.  Indeed, as long as there is a `Server` running, the only constraint is that the `Site` be able to reach the Redis DB (or other backend).

This allows us to do some cool stuff:

 * Run models over confidential data.  The only information shared between machines is higher level parameters
 * Dynamically introduce new data sources into MCMC as they arrive
 * Dynamically allocate computation resources to the most valuable / difficult computations




