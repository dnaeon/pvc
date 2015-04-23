.. _installation:

===================
Installation of PVC
===================

This document walks you through the installation of PVC.

The easiest way to install PVC is by using `pip`_, which would
automatically install any dependencies for you or you could use the
latest development version of PVC from the `Github`_ repository.

Requirements
============

The following list provides information about the PVC dependencies.

* `Python 2.7.x, 3.2.x or later`_
* `humanize`_
* `pythondialog`_
* `pyVmomi`_
* `requests`_
* `vconnector`_

Some of the PVC features require additional packages to be present
in order to take advantage of these features. The list below provides
information about any optional dependencies of PVC.

Note, that these dependencies are not required and are only needed if
you intend to use the features provided by them.

* `gnuplot`_ - Used for plotting performance graphs
* `VMware Player`_ - Used for establishing a remote console session
* A VNC client - Used for establishing a remote console VNC session

Installation with pip
=====================

In order to install PVC using `pip`_, simply execute this command:

.. code-block:: bash

   $ pip install pvc

If you would like to install PVC in a `virtualenv`_, then
follow these steps instead:

.. code-block:: bash

   $ virtualenv pvc-venv
   $ source pvc-venv/bin/activate
   $ pip install pvc

Installation from source
========================

The ``master`` branch of PVC is where main development happens.

In order to install the latest version of PVC follow these
simple steps:

.. code-block:: bash

    $ git clone https://github.com/dnaeon/pvc.git
    $ cd pvc
    $ sudo python setup.py install

If you would like to install PVC in a `virtualenv`_ follow
these steps instead:

.. code-block:: bash

   $ virtualenv pvc-venv
   $ source pvc-venv/bin/activate
   $ git clone https://github.com/dnaeon/pvc.git
   $ cd pvc
   $ python setup.py install

This would take care of installing all dependencies for you
as well.

.. _`pip`: https://pypi.python.org/pypi/pip
.. _`Github`: https://github.com/dnaeon/pvc
.. _`Python 2.7.x, 3.2.x or later`: http://python.org/
.. _`humanize`: https://github.com/jmoiron/humanize
.. _`pythondialog`: http://pythondialog.sourceforge.net/
.. _`pyVmomi`: https://github.com/vmware/pyvmomi
.. _`requests`: http://docs.python-requests.org/en/latest/
.. _`vconnector`: https://github.com/dnaeon/py-vconnector
.. _`gnuplot`: http://www.gnuplot.info/
.. _`VMware Player`: http://www.vmware.com/products/player
.. _`virtualenv`: https://virtualenv.pypa.io/en/latest/


OS Specific Installation
========================

Installing on OSX:

Installing on Ubuntu Linux:
