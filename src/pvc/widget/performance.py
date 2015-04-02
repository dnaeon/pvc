"""
Performance Metric Widgets

"""

import os
import time
import datetime
import tempfile
import subprocess

import pyVmomi
import pvc.widget.menu
import pvc.widget.form
import pvc.widget.checklist

__all__ = ['PerformanceProviderWidget', 'PerformanceCounterWidget']


class PerformanceProviderWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Performance Provider Widget

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
            items=items,
            dialog=self.dialog,
            title=self.obj.name,
            text='Performance Metrics',
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
            dialog=self.dialog,
            form_elements=elements,
            title=self.obj.name,
            text='Performance provider summary information'
        )

        form.display()

    def counter_groups(self):
        """
        Available counter groups for the provider

        """
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        metrics = _get_provider_metrics(self.pm, self.obj)
        if not metrics:
            self.dialog.msgbox(
                title=self.obj.name,
                text='Performance data is currently not available for this entity'
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
            items=items,
            dialog=self.dialog,
            title=self.obj.name,
            text='Select a performance counter group'
        )

        menu.display()

    def counters_in_group(self, label):
        """
        Get counters from a specific group

        Args:
            label (str): Performance counter group label

        """
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        perf_counter = self.pm.perfCounter
        all_metrics = _get_provider_metrics(self.pm, self.obj)
        unique_metrics = set([m.counterId for m in all_metrics])
        counters = [c for c in perf_counter for m in unique_metrics if c.key == m and c.groupInfo.label == label]

        items = [
            pvc.widget.menu.MenuItem(
                tag='{0}.{1}.{2}'.format(c.groupInfo.key, c.nameInfo.key, c.unitInfo.key),
                description=c.nameInfo.summary,
                on_select=PerformanceCounterWidget,
                on_select_args=(self.agent, self.dialog, self.obj, c)
            ) for c in counters
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.obj.name,
            text="Performance counters in group '{}'".format(label)
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

    def _save_performance_samples(self, path, data):
        """
        Save performance samples to a file

        New samples are appended to the file.

        Args:
            path                                      (str): Path to the datafile
            data  (vim.PerformanceManager.EntityMetricBase): The data to be saved

        """
        # The data we save is expected to be retrieved from a single entity
        # TODO: Add support for multiple entities as well
        data = data.pop()
        all_values = [v.value for v in data.value]
        samples = zip(data.sampleInfo, *all_values)

        with open(path, 'a') as f:
            for sample in samples:
                timestamp, values = sample[0].timestamp, sample[1:]
                f.write('{} {}\n'.format(str(timestamp), ' '.join([str(v) for v in values])))

    def _create_gnuplot_script(self, datafile, instances):
        """
        Create a gnuplot(1) script for plotting a graph

        Args:
            datafile   (str): Path to a datafile containing performance samples
            instances (list): A list of object instances present in the performance samples

        Returns:
            Path to the created gnuplot(1) script

        """
        provider_summary = _get_provider_summary(self.pm, self.obj)
        gnuplot_term = os.environ['GNUPLOT_TERMINAL'] if os.environ.get('GNUPLOT_TERMINAL') else 'dumb'

        lines = []
        for index, instance in enumerate(instances):
            l = '"{datafile}" using 1:{index} title "{instance}" with lines'.format(
                datafile=datafile,
                index=index+3,
                instance=instance
            )
            lines.append(l)

        # TODO: Set a time range for the plotted graph
        gnuplot_script_template = """
        # gnuplot(1) script created by PVC
        set title '{name} - {title}'
        set grid
        set terminal {terminal}
        set xdata time
        set timefmt '%Y-%m-%d %H:%M:%S+00:00'
        set format x '%H:%M:%S'
        set xlabel 'Time'
        set ylabel '{unit}'
        set key outside right center
        set autoscale fix
        plot {lines}
        pause {refresh_rate}
        reread
        """

        gnuplot_script = gnuplot_script_template.format(
            name=self.obj.name,
            title=self.counter.nameInfo.summary,
            terminal=gnuplot_term,
            unit=self.counter.unitInfo.label,
            lines=', '.join(lines),
            refresh_rate=provider_summary.refreshRate
        )

        fd, path = tempfile.mkstemp(prefix='pvcgnuplot-script-')
        with open(path, 'w') as f:
            f.write(gnuplot_script)

        return path

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

        title = 'Performance counter {0}.{1}.{2}'.format(
            self.counter.groupInfo.key,
            self.counter.nameInfo.key,
            self.counter.unitInfo.key
        )

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.obj.name,
            text=title
        )

        menu.display()

    def info(self):
        """
        Display information about a counter

        """
        self.dialog.infobox(
            text='Retrieving information ...'
        )

        counter_name = '{0}.{1}.{2}'.format(
            self.counter.groupInfo.key,
            self.counter.nameInfo.key,
            self.counter.unitInfo.key
        )
        intervals = [i.name for i in self.pm.historicalInterval if self.counter.level == i.level]

        elements = [
            pvc.widget.form.FormElement(
                label='Key',
                item=str(self.counter.key)
            ),
            pvc.widget.form.FormElement(
                label='Counter',
                item=counter_name
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
            dialog=self.dialog,
            form_elements=elements,
            title=self.obj.name,
            text='Performance counter information'
        )

        form.display()

    def graph(self):
        """
        Display counter graph using gnuplot(1)

        """
        try:
            p = subprocess.Popen(
                args=['gnuplot', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except OSError as e:
            self.dialog.msgbox(
                title=self.obj.name,
                text='Unable to find gnuplot(1): \n{}\n'.format(e)
            )
            return

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
        checklist_text = 'Select objects for counter {0}.{1}.{2}'.format(
            self.counter.groupInfo.key,
            self.counter.nameInfo.key,
            self.counter.unitInfo.key
        )

        checklist = pvc.widget.checklist.CheckList(
            items=items,
            dialog=self.dialog,
            title=self.obj.name,
            text=checklist_text,
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

        self.dialog.infobox(
            text='Retrieving information ...'
        )

        fd, datafile = tempfile.mkstemp(prefix='pvcgnuplot-data-')

        # TODO: Allow user to choose a custom interval from the past
        #       This query spec is for the initial data set used to plot a
        #       graph for the past hour for our performance counter
        one_hour_ago = self.agent.si.CurrentTime() - datetime.timedelta(seconds=3600)
        query_spec_last_hour = pyVmomi.vim.PerformanceManager.QuerySpec(
            entity=self.obj,
            metricId=metric_id,
            intervalId=provider_summary.refreshRate,
            startTime=one_hour_ago
        )
        data = self.pm.QueryPerf(querySpec=[query_spec_last_hour])
        self._save_performance_samples(
            path=datafile,
            data=data
        )

        # Query spec used to continuously get new performance data
        query_spec = pyVmomi.vim.PerformanceManager.QuerySpec(
            maxSample=1,
            entity=self.obj,
            metricId=metric_id,
            intervalId=provider_summary.refreshRate
        )

        self.dialog.msgbox(
            text='Press CTRL-C to stop plotting graph ...'
        )

        gnuplot_script = self._create_gnuplot_script(
            datafile=datafile,
            instances=selected
        )

        p = subprocess.Popen(
            args=['gnuplot', gnuplot_script]
        )

        try:
            while True:
                data = self.pm.QueryPerf(querySpec=[query_spec])
                self._save_performance_samples(
                    path=datafile,
                    data=data
                )
                time.sleep(provider_summary.refreshRate)
        except KeyboardInterrupt:
            pass

        os.unlink(datafile)
        os.unlink(gnuplot_script)

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
