"""
Performance Metric Widgets

"""

import pyVmomi
import pvc.widget.menu
import pvc.widget.form
import pvc.widget.checklist

__all__ = ['PerformanceProviderWidget', 'PerformanceCounterWidget']


class PerformanceProviderWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Performance Widget

        Args:
            agent         (VConnector): A VConnector instance
            dialog     (dialog.Dialog): A Dialog instance
            obj    (vim.ManagedEntity): A managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.pm = self.agent.si.content.perfManager
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Summary',
                description='Performance provider summary',
                on_select=self.summary
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

    def summary(self):
        """
        Performance provider summary information

        """
        self.dialog.infobox(
            title=self.obj.name,
            text='Retrieving information ...'
        )

        provider_summary = _get_provider_summary(self.pm, self.obj)
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
        Available performance counter groups for the provider

        """
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        metrics = _get_provider_metrics(self.pm, self.obj)
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

        # TODO: Exclude duplicate counters due to the number of multiple instances we might have for a counter
        perf_counter = self.pm.perfCounter
        metrics = _get_provider_metrics(self.pm, self.obj)
        counters = [c for c in perf_counter for m in metrics if c.key == m.counterId and c.groupInfo.label == label]

        items = [
            pvc.widget.menu.MenuItem(
                tag='{0}.{1}.{2}'.format(c.groupInfo.key, c.nameInfo.key, c.unitInfo.key),
                description=c.nameInfo.summary,
                on_select=PerformanceCounterWidget,
                on_select_args=(self.agent, self.dialog, self.obj, c)
            ) for c in counters
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            text="Performance counters in group '{}'".format(label),
            items=items,
            dialog=self.dialog
        )

        menu.display()


class PerformanceCounterWidget(object):
    def __init__(self, agent, dialog, obj, counter):
        """
        Performance Counter Widget

        Args:
            agent                           (VConnector): A VConnector instance
            dialog                       (dialog.Dialog): A Dialog instance
            obj                      (vim.ManagedEntity): A managed entity
            counter (vim.PerformanceManager.CounterInfo): A CounterInfo instance

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.counter = counter
        self.pm = self.agent.si.content.perfManager
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Info',
                description='Counter information',
                on_select=self.info
            ),
            pvc.widget.menu.MenuItem(
                tag='Graph',
                description='Display graph',
                on_select=self.graph
            ),
        ]

        menu = pvc.widget.menu.Menu(
            title=self.obj.name,
            text='Performance counter {0}.{1}.{2}'.format(self.counter.groupInfo.key, self.counter.nameInfo.key, self.counter.unitInfo.key),
            items=items,
            dialog=self.dialog,
            width=70
        )

        menu.display()

    def info(self):
        """
        Display information about a counter

        """
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        intervals = [i.name for i in self.pm.historicalInterval if self.counter.level == i.level]
        elements = [
            pvc.widget.form.FormElement(
                label='Key',
                item=str(self.counter.key)
            ),
            pvc.widget.form.FormElement(
                label='Counter',
                item='{0}.{1}.{2}'.format(self.counter.groupInfo.key, self.counter.nameInfo.key, self.counter.unitInfo.key)
            ),
            pvc.widget.form.FormElement(
                label='Description',
                item=self.counter.nameInfo.summary
            ),
            pvc.widget.form.FormElement(
                label='Group',
                item=self.counter.groupInfo.label
            ),
            pvc.widget.form.FormElement(
                label='Unit',
                item=self.counter.unitInfo.label
            ),
            pvc.widget.form.FormElement(
                label='Intervals',
                item=', '.join(intervals)
            ),
        ]

        form = pvc.widget.form.Form(
            title=self.obj.name,
            text='Performance counter information',
            dialog=self.dialog,
            form_elements=elements
        )

        form.display()

    def graph(self):
        """
        Display counter graph

        """
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        provider_summary = _get_provider_summary(self.pm, self.obj)

        # TODO: Handle historical performance stats as well
        if not provider_summary.currentSupported:
            self.dialog.msgbox(
                text='Entity does not support real-time statistics'
            )
            return

        metrics = [m for m in _get_provider_metrics(self.pm, self.obj) if m.counterId == self.counter.key]
        instances = [m.instance if m.instance else self.obj.name for m in metrics]
        items = [pvc.widget.checklist.CheckListItem(tag=instance) for instance in instances]

        checklist = pvc.widget.checklist.CheckList(
            title=self.obj.name,
            text='Select objects for counter {0}.{1}.{2}'.format(self.counter.groupInfo.key, self.counter.nameInfo.key, self.counter.unitInfo.key),
            items=items,
            dialog=self.dialog
        )
        checklist.display()
        selected = checklist.selected()

        if not selected:
            self.dialog.msgbox(
                text='No objects selected'
            )
            return

        metric_id = [
            pyVmomi.vim.PerformanceManager.MetricId(
                counterId=self.counter.key,
                instance='' if instance == self.obj.name else instance
            ) for instance in selected
        ]

        # TODO: Initially plot the graph for the last 1 hour
        query_spec = pyVmomi.vim.PerformanceManager.QuerySpec(
            maxSample=1,
            entity=self.obj,
            metricId=metric_id,
            intervalId=provider_summary.refreshRate
        )

        # TODO: Make this work for all selected instances as it takes only the first one now
        #data = self.pm.QueryPerf(
        #    querySpec=[query_spec]
        #)
        #value = data[0].value[0].value[0]


def _get_provider_summary(pm, obj):
    """
    Get performance provider summary information

    Args:
        pm  (vim.PerformanceManager): A PerformanceManager instance
        obj      (vim.ManagedEntity): A ManagedEntity to be queried

    """
    return pm.QueryPerfProviderSummary(entity=obj)

def _get_provider_metrics(pm, obj):
    """
    Get available metrics for a performance provider

    Args:
        pm  (vim.PerformanceManager): A PerformanceManager instance
        obj      (vim.ManagedEntity): A ManagedEntity to be queried

    """
    provider_summary = _get_provider_summary(pm, obj)
    refresh_rate = provider_summary.refreshRate if provider_summary.currentSupported else None
    metric_id = pm.QueryAvailablePerfMetric(
        entity=obj,
        intervalId=refresh_rate
    )

    return metric_id
