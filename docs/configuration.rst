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


VMware(R) Player for Console Support
====================================

If the vmplayer binary is in your $PATH variable pvc should be capable
of launching the VMware(R) Player for connecting to remote consoles
on a host.

.. _ `VMware Player`: http://www.vmware.com/products/player

VNC Console Support
===================



Debugging Output
================

