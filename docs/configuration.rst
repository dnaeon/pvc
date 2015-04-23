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

VNC Console Support
===================

PVC supports launching of VNC console to a Virtual Machine, but you
need to make sure that certain ports on the ESXi hosts are opened, so
that a successful VNC connection can be established.

PVC uses ports 5901-5999 for establishing a VNC connection to a
Virtual Machine.

Refer `How to Create Custom Firewall Rules in ESXi 5.0`_ article
for more information on how to manage the firewall rules on your
VMware ESXi hosts and open the required ports for VNC communication.

Debugging Output
================

.. _`gnuplot`: http://www.gnuplot.info/
.. _`VMRC`: https://www.vmware.com/go/download-vmrc
.. _ `VMware Player`: http://www.vmware.com/products/player
.. _`KB 2091284`: http://kb.vmware.com/kb/2091284
.. _`How to Create Custom Firewall Rules in ESXi 5.0`: http://www.virtuallyghetto.com/2011/07/how-to-create-custom-firewall-rules-in.html
