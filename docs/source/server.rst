.. DistSamp documentation master file, created by
   sphinx-quickstart on Sun May 20 09:50:14 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Server
====================================

The role of the server is to take care of allowing the `Site`s to work together.  It takes care of both aggregating the `Site` approximations into a complete posterior and providing the `Site`s with their cavity distributions.

Architecturally, the `Server` is completely decoupled away from the running of any `Site`.  As long as the `Server` can talk to the underlying redis DB, then it can run from any location.

It's clear that the `Server` is a potential choke point for the whole system, if it can't keep up with `Site` updates, then no communication between `Site`s is possible.  This problem is offset by a number of factors:
    * for most use cases their will be relatively few `Site`s
    * the computation of the `Server` is very low compared to that done by `Site`s
    * the `Server` component can be horizontally scaled by adding more instances

Contents:

.. toctree::
   :maxdepth: 2

