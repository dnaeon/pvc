"""
Performance Metric Widgets

"""

import pyVmomi
import pvc.widget.menu
import pvc.widget.form

__all__ = ['PerformanceWidget']


class PerformanceWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Performance Widget

        Args:
            agent                 (VConnector): A VConnector instance
            dialog             (dialog.Dialog): A Dialog instance
            obj    (pyVmomi.vim.ManagedEntity): A managed entity

        """
        if not isinstance(obj, pyVmomi.vim.ManagedEntity):
            raise TypeError('Need a vim.ManagedEntity instance')

        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.pm = self.agent.si.content.perfManager
        self.display()

    def _get_provider_summary(self):
        """
        Get provider summary information

        """
        return self.pm.QueryPerfProviderSummary(entity=self.obj)

    def _get_provider_metrics(self):
        """
        Get the available metrics for the provider

        """
        provider_summary = self._get_provider_summary()
        refresh_rate = provider_summary.refreshRate if provider_summary.currentSupported else None
        metric_id = self.pm.QueryAvailablePerfMetric(
            entity=self.obj,
            intervalId=refresh_rate
        )

        return metric_id

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Summary',
                description='Performance provider summary',
                on_select=self.provider_summary
            ),
            pvc.widget.menu.MenuItem(
                tag='Metrics',
                description='Available performance metrics',
                on_select=self.metrics
            ),
            pvc.widget.menu.MenuItem(
                tag='Real-time',
                description='Real-time performance metrics'
            ),
            pvc.widget.menu.MenuItem(
                tag='Historical',
                description='Historical performance metrics'
            ),
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            text='Performance Metrics',
            items=items,
            dialog=self.dialog
        )
        menu.display()

    def summary(self):
        """
        Performance provider summary information

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving information ...'
        )

        provider_summary = self.pm.QueryPerfProviderSummary(
            entity=self.obj
        )

        elements = [
            pvc.widget.form.FormElement(
                label='Real-time statistics support',
                item=str(provider_summary.currentSupported)
            ),
            pvc.widget.form.FormElement(
                label='Historical statistics support',
                item=str(provider_summary.summarySupported)
            ),
            pvc.widget.form.FormElement(
                label='Refresh rate (seconds)',
                item=str(provider_summary.refreshRate)
            )
        ]

        form = pvc.widget.form.Form(
            title=self.obj.name,
            text='Performance provider summary information',
            form_elements=elements
            dialog=self.dialog,
        )

        form.display()

