.. DistSamp documentation master file, created by
   sphinx-quickstart on Sun May 20 09:50:14 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Data
====

The ``Data`` class encapsulates the data associated with a ``Site``.  Its main purpose is to provide a consistent way to run approximation methods on different sources of data, e.g. Spark or pandas dataframes.  This way, a ``Site`` can deal with data in an abstracted way.  Indeed, ``Models`` can be composed out of wildly varying sources of data.

.. autoclass:: distsamp.data.data.Data


.. toctree::
   :maxdepth: 2

