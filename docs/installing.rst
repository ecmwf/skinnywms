.. _installing:

Installing
==========


Pip install
-----------

To install **skinnywms**, just run the following command:

.. code-block:: bash

  pip install skinnywms

The skinnywms ``pip`` package has been tested successfully with the latest versions of
its dependencies (`build logs <https://github.com/ecmwf/magpye/actions/workflows/test-and-release.yml>`_).

Conda install
-------------
.. code-block:: bash

  conda config --add channels conda-forge
  conda install skinnywms


.. note::

  Mixing ``pip`` and ``conda`` could create some dependencies issues,
  we recommend installing as many dependencies as possible with conda,
  then install magpye with ``pip``, `as recommended by the anaconda team
  <https://www.anaconda.com/blog/using-pip-in-a-conda-environment>`_.


Troubleshooting
---------------

Python 3.7 or above is required
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  skinnywms requires Python 3.7 or above. Depending on your installation,
  you may need to substitute ``pip`` to ``pip3`` in the examples below.

  .. todo::

    Python 3.10 is not supported yet,
    as some dependencies are not available for python 3.10.


