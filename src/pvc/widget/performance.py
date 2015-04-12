# Copyright (c) 2015 Marin Atanasov Nikolov <dnaeon@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer
#    in this position and unchanged.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR(S) ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR(S) BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Performance Metrics Widgets

"""

import os
import datetime
import tempfile
import subprocess

import pyVmomi

import pvc.widget.menu
import pvc.widget.form
import pvc.widget.checklist
import pvc.widget.radiolist

__all__ = [
    'PerformanceProviderWidget', 'PerformanceGroupWidget',
    'PerformanceCounterInGroupWidget', 'PerformanceCounterWidget',
    'PerformanceCounterGraphWidget',
]


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
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
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
                on_select=PerformanceGroupWidget,
                on_select_args=(self.agent, self.dialog, self.obj)
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select an item from the menu',
        )

        menu.display()

    def summary(self):
        """
        Performance provider summary information

        """
        self.dialog.infobox(
            title=self.title,
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
            dialog=self.dialog,
            form_elements=elements,
            title=self.title,
            text='Performance provider summary information'
        )

        form.display()


class PerformanceGroupWidget(object):
    def __init__(self, agent, dialog, obj):
        """
        Displays a menu of available counter groups for the provider

        Args:
            agent         (VConnector): A VConnector instance
            dialog     (dialog.Dialog): A Dialog instance
            obj    (vim.ManagedEntity): A managed entity

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.pm = self.agent.si.content.perfManager
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        items = [
            pvc.widget.menu.MenuItem(
                tag='Real-time',
                description='Real-time performance metrics',
                on_select=self.realtime_counter_groups
            ),
            pvc.widget.menu.MenuItem(
                tag='Historical',
                description='Historical performance metrics',
                on_select=self.historical_counter_groups
            ),
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select an item from the menu',
        )

        menu.display()

    def realtime_counter_groups(self):
        """
        Available real-time counter groups

        """
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        provider_summary = self.pm.QueryPerfProviderSummary(
            entity=self.obj
        )

        if not provider_summary.currentSupported:
            self.dialog.msgbox(
                title=self.title,
                text='Provider does not support real-time statistics'
            )
            return

        metric_id = self.pm.QueryAvailablePerfMetric(
            entity=self.obj,
            intervalId=provider_summary.refreshRate
        )

        if not metric_id:
            self.dialog.msgbox(
                title=self.title,
                text='Performance data is currently not available for entity'
            )
            return

        perf_counter = self.pm.perfCounter
        counters = [c for c in perf_counter for m in metric_id if c.key == m.counterId]
        groups = set([(c.groupInfo.key, c.groupInfo.label) for c in counters])

        items = [
            pvc.widget.menu.MenuItem(
                tag=key,
                description=label,
                on_select=PerformanceCounterInGroupWidget,
                on_select_args=(self.agent, self.dialog, self.obj, metric_id, label, True)
            ) for key, label in groups
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select a performance counter group'
        )

        menu.display()

    def historical_counter_groups(self):
        """
        Available historical counter groups

        """
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        provider_summary = self.pm.QueryPerfProviderSummary(
            entity=self.obj
        )

        if not provider_summary.summarySupported:
            self.dialog.msgbox(
                title=self.title,
                text='Provider does not support historical statistics'
            )
            return

        metric_id = self.pm.QueryAvailablePerfMetric(
            entity=self.obj
        )

        if not metric_id:
            self.dialog.msgbox(
                title=self.title,
                text='Performance data is currently not available for entity'
            )
            return

        perf_counter = self.pm.perfCounter
        counters = [c for c in perf_counter for m in metric_id if c.key == m.counterId]
        groups = set([(c.groupInfo.key, c.groupInfo.label) for c in counters])

        items = [
            pvc.widget.menu.MenuItem(
                tag=key,
                description=label,
                on_select=PerformanceCounterInGroupWidget,
                on_select_args=(self.agent, self.dialog, self.obj, metric_id, label, False)
            ) for key, label in groups
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select a performance counter group'
        )

        menu.display()


class PerformanceCounterInGroupWidget(object):
    def __init__(self, agent, dialog, obj, metric_id, label, realtime):
        """
        Display a menu of available performance counters
        in specific performance group

        Args:
            agent         (VConnector): A VConnector instance
            dialog     (dialog.Dialog): A Dialog instance
            obj    (vim.ManagedEntity): A managed entity
            metric_id           (list): A list of vim.PerformanceManager.MetricId instances,
                                        retrieved by a previous
                                        vim.PerformanceManager.QueryAvailablePerfMetric() call
            label                (str): Performance counter group label
            realtime            (bool): A flag indicating that this counter group contains
                                        real-time counters if set to True. Otherwise consider
                                        counters from this group as historical.

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.pm = self.agent.si.content.perfManager
        self.metric_id = metric_id
        self.label = label
        self.realtime = realtime
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        # Get the unique metrics so we don't get duplicate
        # entries in the resulting menu. Duplicate entries
        # may be seen by counters with more than one
        # object instance, e.g. vmnic0, vmnic1, etc.
        unique_metrics = set([m.counterId for m in self.metric_id])

        perf_counter = self.pm.perfCounter
        counters = [c for c in perf_counter for m in unique_metrics if c.key == m and c.groupInfo.label == self.label]

        items = [
            pvc.widget.menu.MenuItem(
                tag='{0}.{1}.{2}'.format(c.groupInfo.key, c.nameInfo.key, c.unitInfo.key),
                description=c.nameInfo.label,
                on_select=PerformanceCounterWidget,
                on_select_args=(self.agent, self.dialog, self.obj, c, self.realtime)
            ) for c in counters
        ]

        menu = pvc.widget.menu.Menu(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text="Performance counters in group '{}'".format(self.label)
        )

        menu.display()


class PerformanceCounterWidget(object):
    def __init__(self, agent, dialog, obj, counter, realtime):
        """
        Performance Counter Widget

        Args:
            agent                           (VConnector): A VConnector instance
            dialog                       (dialog.Dialog): A Dialog instance
            obj                      (vim.ManagedEntity): A managed entity
            counter (vim.PerformanceManager.CounterInfo): A CounterInfo instance
            realtime                              (bool): A flag indicating that this
                                                          counter has been retrieved
                                                          from a real-time counter group if
                                                          set to True. Otherwise we consider
                                                          this counter as retrieved from a
                                                          historical counter group

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.counter = counter
        self.realtime = realtime
        self.pm = self.agent.si.content.perfManager
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
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
                on_select=PerformanceCounterGraphWidget,
                on_select_args=(self.agent, self.dialog, self.obj, self.counter, self.realtime)
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
            title=self.title,
            text=title
        )

        menu.display()

    def info(self):
        """
        Display information about a counter

        """
        self.dialog.infobox(
            title=self.title,
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
                label='Label',
                item=self.counter.nameInfo.label
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
            title=self.title,
            text='Performance counter information'
        )

        form.display()


class PerformanceCounterGraphWidget(object):
    def __init__(self, agent, dialog, obj, counter, realtime):
        """
        Widget to plot a gnuplot(1) graph of a performance counter

        Args:
            agent                           (VConnector): A VConnector instance
            dialog                       (dialog.Dialog): A Dialog instance
            obj                      (vim.ManagedEntity): A managed entity
            counter (vim.PerformanceManager.CounterInfo): A CounterInfo instance
            realtime                              (bool): A flag indicating that this
                                                          counter has been retrieved
                                                          from a real-time counter group if
                                                          set to True. Otherwise we consider
                                                          this counter as retrieved from a
                                                          historical counter group

        """
        self.agent = agent
        self.dialog = dialog
        self.obj = obj
        self.counter = counter
        self.realtime = realtime
        self.pm = self.agent.si.content.perfManager
        self.title = '{} ({})'.format(self.obj.name, self.obj.__class__.__name__)
        self.display()

    def display(self):
        try:
            subprocess.Popen(
                args=['gnuplot', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except OSError as e:
            self.dialog.msgbox(
                title=self.title,
                text='Unable to find gnuplot(1): \n{}\n'.format(e)
            )
            return

        selected_instances = self.select_counter_instances()
        if not selected_instances:
            self.dialog.msgbox(
                title=self.title,
                text='No counter instances selected'
            )
            return

        metric_id = [
            pyVmomi.vim.PerformanceManager.MetricId(
                counterId=self.counter.key,
                instance='' if instance == self.obj.name else instance
            ) for instance in selected_instances
        ]

        fd, datafile = tempfile.mkstemp(prefix='pvcgnuplot-data-')
        script = self.create_gnuplot_script(
            datafile=datafile,
            instances=selected_instances
        )

        if self.realtime:
            self.realtime_graph(metric_id, datafile, script)
        else:
            self.historical_graph(metric_id, datafile, script)

        os.unlink(datafile)
        os.unlink(script)

    def save_performance_samples(self, path, data):
        """
        Save performance samples to a file

        New samples are appended to the file

        NOTE: If the performance counter unit is percentage we need
              to make sure that the sample value is divided by
              a hundred, as the returned sample value
              represents a 1/100th of the percent.

        Args:
            path                                      (str): Path to the datafile
            data  (vim.PerformanceManager.EntityMetricBase): The data to be saved

        """
        all_values = [v.value for v in data.value]
        samples = zip(data.sampleInfo, *all_values)

        with open(path, 'a') as f:
            for sample in samples:
                timestamp, values = sample[0].timestamp, sample[1:]
                if self.counter.unitInfo.key == 'percent':
                    f.write('{},{}\n'.format(str(timestamp), ','.join([str(v / 100) for v in values])))
                else:
                    f.write('{},{}\n'.format(str(timestamp), ','.join([str(v) for v in values])))

    def create_gnuplot_script(self, datafile, instances):
        """
        Create a gnuplot(1) script for plotting a graph

        Args:
            datafile   (str): Path to a datafile containing performance samples
            instances (list): A list of object instances present in the
                              retrieved performance samples, e.g. vmnic0, vmnic1, etc.

        Returns:
            Path to the created gnuplot(1) script

        """
        gnuplot_term = os.environ['GNUPLOT_TERM'] if os.environ.get('GNUPLOT_TERM') else 'dumb'

        lines = []
        for index, instance in enumerate(instances):
            l = '"{datafile}" using 1:{index} title "{instance}" with lines'.format(
                datafile=datafile,
                index=index+2,
                instance=instance
            )
            lines.append(l)

        script_template = (
            "# gnuplot(1) script created by PVC\n"
            "set title '{name} - {title}'\n"
            "set term {term}\n"
            "set grid\n"
            "set xdata time\n"
            "set timefmt '%Y-%m-%d %H:%M:%S+00:00'\n"
            "# set format x '%H:%M:%S'\n"
            "set xlabel 'Time'\n"
            "set ylabel '{unit}'\n"
            "set key outside right center\n"
            "set datafile separator ','\n"
            "set autoscale fix\n"
            "set yrange [{yrange}]\n"
            "plot {lines}\n"
            "pause {pause}\n"
        )

        # Real-time counters
        # Append any additional gnuplot(1) commands here
        # for real-time counters
        if self.realtime:
            provider_summary = self.pm.QueryPerfProviderSummary(
                entity=self.obj
            )
            pause = provider_summary.refreshRate

            # Append the 'reread' gnuplot(1) command
            script_template += 'reread\n'
        else:
            # Historical counters
            pause = -1

        # Set a yrange for counters which unit is percentage
        yrange = '0:100' if self.counter.unitInfo.key == 'percent' else ''

        gnuplot_script = script_template.format(
            name=self.obj.name,
            title=self.counter.nameInfo.summary,
            term=gnuplot_term,
            unit=self.counter.unitInfo.label,
            lines=', '.join(lines),
            pause=pause,
            yrange=yrange
        )

        fd, path = tempfile.mkstemp(prefix='pvcgnuplot-script-')
        with open(path, 'w') as f:
            f.write(gnuplot_script)

        return path

    def select_counter_instances(self):
        """
        Prompts the user to select counter instances

        """
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        if self.realtime:
            provider_summary = self.pm.QueryPerfProviderSummary(
                entity=self.obj
            )
            interval_id = provider_summary.refreshRate
        else:
            interval_id = None

        metric_id = self.pm.QueryAvailablePerfMetric(
            entity=self.obj,
            intervalId=interval_id
        )
        metrics = [m for m in metric_id if m.counterId == self.counter.key]
        instances = [m.instance if m.instance else self.obj.name for m in metrics]
        items = [
            pvc.widget.checklist.CheckListItem(tag=instance)
            for instance in instances
        ]
        checklist_text = 'Select instances for counter {0}.{1}.{2}'.format(
            self.counter.groupInfo.key,
            self.counter.nameInfo.key,
            self.counter.unitInfo.key
        )

        checklist = pvc.widget.checklist.CheckList(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text=checklist_text,
        )
        checklist.display()

        return checklist.selected()

    def select_historical_interval(self):
        """
        Prompts the user to select an existing historical interval

        """
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        intervals = [i.name for i in self.pm.historicalInterval]
        items = [
            pvc.widget.radiolist.RadioListItem(tag=interval) for interval in intervals
        ]

        radiolist = pvc.widget.radiolist.RadioList(
            items=items,
            dialog=self.dialog,
            title=self.title,
            text='Select a historical performance interval',
        )

        return radiolist.display()

    def realtime_graph(self, metric_id, datafile, script):
        """
        Plot a real-time graph

        Args:
            metric_id (list): A list of vim.PerformanceManager.MetricId instances
            datafile   (str): Path to a datafile to store collected samples
            script     (str): Path to a gnuplot(1) script used to plot the graph

        """
        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        provider_summary = self.pm.QueryPerfProviderSummary(
            entity=self.obj
        )
        interval_id = provider_summary.refreshRate

        # Query spec to get data from the past hour
        one_hour_ago = self.agent.si.CurrentTime() - datetime.timedelta(seconds=3600)
        query_spec_last_hour = pyVmomi.vim.PerformanceManager.QuerySpec(
            entity=self.obj,
            metricId=metric_id,
            intervalId=interval_id,
            startTime=one_hour_ago
        )
        data = self.pm.QueryPerf(querySpec=[query_spec_last_hour]).pop()
        self.save_performance_samples(
            path=datafile,
            data=data
        )

        # Query spec used to continuously get new performance data
        query_spec = pyVmomi.vim.PerformanceManager.QuerySpec(
            maxSample=1,
            entity=self.obj,
            metricId=metric_id,
            intervalId=interval_id
        )

        p = subprocess.Popen(
            args=['gnuplot', script]
        )

        text = (
            'Graph updates every {} seconds.\n\n'
            'Press CANCEL in order to stop plotting the '
            'graph and exit.\n'
        )

        while True:
            data = self.pm.QueryPerf(querySpec=[query_spec]).pop()
            self.save_performance_samples(
                path=datafile,
                data=data
            )
            code = self.dialog.pause(
                title=self.title,
                text=text.format(interval_id),
                height=15,
                width=60,
                seconds=interval_id
            )
            if code == self.dialog.CANCEL:
                break

        p.terminate()

    def historical_graph(self, metric_id, datafile, script):
        """
        Plot a historical graph

        Args:
            metric_id (list): A list of vim.PerformanceManager.MetricId instances
            datafile   (str): Path to a datafile to store collected samples
            script     (str): Path to a gnuplot(1) script used to plot the graph

        """
        code, interval = self.select_historical_interval()
        if code in (self.dialog.CANCEL, self.dialog.ESC) or not interval:
            return

        self.dialog.infobox(
            title=self.title,
            text='Retrieving information ...'
        )

        interval_id = [i.samplingPeriod for i in self.pm.historicalInterval if i.name == interval].pop()
        query_spec = pyVmomi.vim.PerformanceManager.QuerySpec(
            entity=self.obj,
            metricId=metric_id,
            intervalId=interval_id
        )
        data = self.pm.QueryPerf(querySpec=[query_spec]).pop()
        self.save_performance_samples(
            path=datafile,
            data=data
        )

        p = subprocess.Popen(
            args=['gnuplot', script]
        )

        p.wait()
