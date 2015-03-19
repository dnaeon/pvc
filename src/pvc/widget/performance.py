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
                tag='Groups',
                description='Performance counter groups',
                on_select=self.counter_groups
            ),
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            text='Performance Metrics',
            items=items,
            dialog=self.dialog
        )
        menu.display()

    def provider_summary(self):
        """
        Performance provider summary information

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving information ...'
        )

        provider_summary = self._get_provider_summary()
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
            form_elements=elements,
            dialog=self.dialog
        )

        form.display()

    def counter_groups(self):
        """
        Available performance counter groups for this provider

        """
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        metrics = self._get_provider_metrics()
        if not metrics:
            self.dialog.msgbox(
                title=self.obj.name,
                text='Performance data is currently not available for this entity',
                width=70
            )
            return

        perf_counter = self.pm.perfCounter
        counters = [c for c in perf_counter for m in metrics if c.key == m.counterId]
        groups = [(c.groupInfo.key, c.groupInfo.label) for c in counters]

        items = [
            pvc.widget.menu.MenuItem(
                tag=key,
                description=label,
                on_select=self.counters_in_group,
                on_select_args=(label,)
            ) for key, label in set(groups)
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            text='Select a performance counter group',
            items=items,
            dialog=self.dialog
        )

        menu.display()

    def counters_in_group(self, label):
        """
        Get counters from a specific counter group

        Args:
            label (str): Performance counter group label

        """
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        perf_counter = self.pm.perfCounter
        metrics = self._get_provider_metrics()
        counters = [c for c in perf_counter for m in metrics if c.key == m.counterId and c.groupInfo.label == label]

        items = [
            pvc.widget.menu.MenuItem(
                tag='{0}.{1}.{2}'.format(c.groupInfo.key, c.nameInfo.key, c.unitInfo.key),
                description=c.nameInfo.summary,
            ) for c in counters
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            text="Performance counters in group '{}'".format(label),
            items=items,
            dialog=self.dialog
        )

        menu.display()

