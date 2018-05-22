.. DistSamp documentation master file, created by
   sphinx-quickstart on Sun May 20 09:50:14 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Model
=====

`Model`s exist to make the process of coordinating `Server`s and `Site`s easier.  They are extremely useful for running models where all of the data is known ahead of time and can be easy encapsulated in data classes.  Conveniently, this is most use cases.

Models require three pieces of information:

    - the name of the model
    - a prior to use
    - a list of `Site`s contained in the model

Based on this information, `Model`s allow us to a number of ways to run approximations

    - run single iterations
    - run multiple rounds of iteration
    - run until convergence

Models don't know anything about how `Site`s run their own approximations, so they can't control where the approximations are run, but different `Model` classes coordinate the `Site` approximation in different ways depending on use case:

    - local server, serial updating steps => useful for debugging and testing
    - local server, parallel updating steps => useful for quick running locally or on a cluster
    - spark server, parallel updating steps => useful if your only infrastructure is a spark cluster

.. autoclass:: distsamp.model.model.Model

.. toctree::
   :maxdepth: 2