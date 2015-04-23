.. _configuration:

====================
Configuration of PVC
====================

By default PVC does not require any special configuration to work.

Gnuplot Configuration Options
=============================

If you are using `gnuplot`_ for plotting perfomance graphs with PVC
and you want to customize the `gnuplot`_ terminal being used you could
set the ``GNUPLOT_TERM`` environment variable to your desired terminal.

If ``GNUPLOT_TERM`` is not set then PVC will use a ``dumb`` terminal
when plotting a performance graph.

.. _`gnuplot`: http://www.gnuplot.info/


VMRC Console Support
====================

Launching a remote console to a Virtual Machine requires that you
have `VMRC`_ installed on your system.

Currently `VMRC`_ support is pvovided by VMware for Windows(R) and
Mac OS X systems and support for GNU/Linux is underway.

`VMRC`_ support for GNU/Linux is planned, but not yet available, so
in order to launch a console to a Virtual Machine from a GNU/Linux
system you need to use `VMware Player`_ for now.

Check `KB 2091284`_ for more details on the `VMRC`_ support.

.. _`VMRC`: https://www.vmware.com/go/download-vmrc
.. _ `VMware Player`: http://www.vmware.com/products/player
.. _`KB 2091284`: http://kb.vmware.com/kb/2091284

VNC Console Support
===================



Debugging Output
================

