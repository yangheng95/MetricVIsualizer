# -*- coding: utf-8 -*-
# file: metric_visualizer.py
# time: 03/02/2022
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.
import os.path
import random
import shlex
import subprocess
from collections import OrderedDict

import matplotlib.colors
import numpy as np
import tikzplotlib
from findfile import find_cwd_files
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import iqr
from tabulate import tabulate


def legend_without_duplicate_labels(ax):
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    ax.legend(*zip(*unique))


class MetricVisualizer:
    COLORS_DICT = matplotlib.colors.XKCD_COLORS
    COLORS_DICT.update(matplotlib.colors.CSS4_COLORS)
    COLORS = list(COLORS_DICT.values())
    # MARKERS = matplotlib.markers
    MARKERS = [".", "o", "v", "^", "<", ">",
               "1", "2", "3", "4", "8", "s",
               "p", "P", "*", "h", "H", "+",
               "x", "X", "D", "d", "|", "_",
               0, 1, 2, 4, 5, 6, 7, 8, 9, 10,
               11, "None", " ", ""]

    HATCHES = ['/', '\\', '|', '-', '+', 'x',
               'o', 'O', '.', '*']

    box_plot_tex_template = r"""
    \documentclass{article}
    \usepackage{pgfplots}
    \usepackage{tikz}
    \usepackage{caption}
    \usetikzlibrary{intersections}
    \usepackage{helvet}
    \usepackage[eulergreek]{sansmath}
    \usepackage{amsfonts,amssymb,amsmath,amsthm,amsopn}	% math related

    \begin{document}
        \pagestyle{empty}
        \pgfplotsset{ compat=1.12,every axis/.append style={
            grid = major,
            thick,
            xtick={$xtick$},
            xticklabels={$xticklabel$},
            ylabel = {$ylabel$},
            ylabel style={font=\Large},
            xlabel = {$xlabel$},
            xlabel style={font=\Large},
            x tick label style={rotate=0,anchor=north},
            y tick label style={rotate=0,anchor=east},
            xticklabel shift=1pt,
            line width = 1pt,
            tick style = {line width = 0.8pt}}}
        \pgfplotsset{every plot/.append style={thin}}


        \begin{figure}
        \centering

        $tikz_code$

        \end{figure}

    \end{document}
    """

    violin_plot_tex_template = r"""
    \documentclass{article}
    \usepackage{pgfplots}
    \usepackage{tikz}
    \usepackage{caption}
    \usetikzlibrary{intersections}
    \usepackage{helvet}
    \usepackage[eulergreek]{sansmath}
    \usepackage{amsfonts,amssymb,amsmath,amsthm,amsopn}	% math related

    \begin{document}
        \pagestyle{empty}
        \pgfplotsset{ compat=1.12,every axis/.append style={
            grid = major,
            thick,
            xticklabels={$xticklabel$},
            xtick={$xtick$},
            ylabel = {$ylabel$},
            ylabel style={font=\Large},
            xlabel = {$xlabel$},
            xlabel style={font=\Large},
            x tick label style={rotate=0,anchor=north},
            y tick label style={rotate=0,anchor=east},
            xticklabel shift=1pt,
            line width = 1pt,
            tick style = {line width = 0.8pt}}}
        \pgfplotsset{every plot/.append style={thin}}


        \begin{figure}
        \centering

        $tikz_code$

        \end{figure}

    \end{document}
    """

    traj_plot_tex_template = r"""
    \documentclass{article}
    \usepackage{pgfplots}
    \usepackage{tikz}
    \usetikzlibrary{intersections}
    \usepackage{helvet}
    \usepackage[eulergreek]{sansmath}

    \begin{document}
        \pagestyle{empty}
        \pgfplotsset{every axis/.append style={
            grid = major,
            thick,
            xtick={$xtick$},
            xticklabels={$xticklabel$},
            xlabel = {$xlabel$},
            xlabel style={font=\Large},
            x tick label style={rotate=0,anchor=north},
            y tick label style={rotate=0,anchor=east},
            ylabel = {$ylabel$},
            ylabel style={font=\Large},
            xticklabel shift=1pt,
            line width = 1pt,
            tick style = {line width = 0.8pt}}
        }
        \pgfplotsset{every plot/.append style={very thin}}


        \begin{figure}
        \centering

        $tikz_code$

        \end{figure}

    \end{document}
"""

    def set_box_plot_tex_template(self, box_plot_tex_template):
        self.box_plot_tex_template = box_plot_tex_template

    def set_violin_plot_tex_template(self, box_violin_tex_template):
        self.box_plot_tex_template = box_violin_tex_template

    def set_traj_plot_tex_template(self, box_traj_tex_template):
        self.box_plot_tex_template = box_traj_tex_template

    def __init__(self, metric_dict=None):
        """
        Used for plotting, e.g.,
            'Metric1': {
                'trail-0': [77.06, 2.52, 35.14, 3.04, 77.29, 3.8, 57.4, 38.52, 60.36, 22.45],
                'train-1': [64.53, 58.33, 97.89, 68.12, 88.6, 60.33, 70.99, 75.91, 42.49, 15.03],
                'train-2': [97.74, 86.05, 41.34, 81.66, 75.08, 1.76, 94.63, 27.26, 47.11, 42.06],
            },
            'Metric2': {
                'trail-0': [111.5, 105.61, 179.08, 167.25, 181.85, 152.75, 194.82, 130.86, 108.51, 151.44] ,
                'train-1': [187.58, 106.35, 134.22, 167.68, 188.24, 196.54, 154.21, 193.71, 183.34, 150.18],
                'train-2': [159.24, 148.44, 119.49, 160.24, 169.6, 133.27, 129.36, 180.36, 165.24, 152.38],
            }

        :param metric_dict: If you want to plot figure, it is recommended to add multiple trail experiments. In these trial, the experimental results
        are comparative, e.g., just minor different in these experiments.
        """
        if metric_dict is None:
            self.metrics = OrderedDict(
                {
                    # 'Metric1': {
                    #     'trail-0': [80.41, 79.78, 81.03, 80.09, 79.62, 80.56, 80.88, 79.94, 79.47, 79.78, 80.72, 79.78, 81.35, 80.88, 81.03],
                    #     'train-1': [80.41, 79.78, 81.03, 80.09, 79.62, 80.56, 80.88, 79.94, 79.47, 79.78, 80.72, 79.78, 81.35, 80.88, 81.03],
                    #     'train-2': [80.41, 79.78, 81.03, 80.09, 79.62, 80.56, 80.88, 79.94, 79.47, 79.78, 80.72, 79.78, 81.35, 80.88, 81.03],
                    # },
                    # 'Metric2': {
                    #     'trail-0': [76.79, 75.49, 77.92, 77.21, 75.63, 76.96, 77.44, 76.26, 76.35, 76.12, 76.12, 76.78, 75.64, 77.31, 73.79],
                    #     'train-1': [76.79, 75.49, 77.92, 77.21, 75.63, 76.96, 77.44, 76.26, 76.35, 76.12, 76.12, 76.78, 75.64, 77.31, 73.79],
                    #     'train-2': [76.79, 75.49, 77.92, 77.21, 75.63, 76.96, 77.44, 76.26, 76.35, 76.12, 76.12, 76.78, 75.64, 77.31, 73.79],
                    # }
                })
        else:
            self.metrics = metric_dict

        self.trail_id = 0

    def next_trail(self):
        self.trail_id += 1

    def add_metric(self, metric_name='Accuracy', value=0):
        if metric_name in self.metrics:
            if 'trail-{}'.format(self.trail_id) not in self.metrics[metric_name]:
                self.metrics[metric_name]['trail-{}'.format(self.trail_id)] = [value]
            else:
                self.metrics[metric_name]['trail-{}'.format(self.trail_id)].append(value)
        else:
            self.metrics[metric_name] = {'trail-{}'.format(self.trail_id): [value]}

    def traj_plot(self, save_path=None, **kwargs):

        def fix_tex_traj_plot_legend(tex_src_str, metrics):
            for metric_name in metrics.keys():
                tex_src_str = tex_src_str.replace('\\addlegendentry{' + metric_name + '}', '', len(metrics[metric_name]) - 1)
            point_first_addplot = tex_src_str.find('\\addplot')
            point_end_axis = tex_src_str.find('\\end{axis')
            point_first_addlegend = tex_src_str.find("\\addlegend")
            point_switch = point_first_addlegend - tex_src_str[point_first_addplot + 1:point_first_addlegend + 1][::-1].find('\\addplot'[::-1]) - len('\\addplot')

            tex_src_str = tex_src_str[:point_first_addplot] + tex_src_str[point_switch:point_end_axis] + tex_src_str[point_first_addplot:point_switch] + tex_src_str[point_end_axis:]

            return tex_src_str

        alpha = kwargs.pop('alpha', 0.01)

        markersize = kwargs.pop('markersize', 3)

        xticks = kwargs.pop('xticks', '')

        xlabel = kwargs.pop('xlabel', '')

        ylabel = kwargs.pop('ylabel', '')

        linewidth = kwargs.pop('linewidth', 0.5)

        hatches = kwargs.pop('hatches', None)

        fontsize = kwargs.pop('fontsize', 12)

        rotation = kwargs.pop('rotation', 0)

        for metric_name in self.metrics.keys():
            ax = plt.subplot()
            metrics = self.metrics[metric_name]

            x = [i for i, label in enumerate(metrics)]
            y = np.array([metrics[metric_name] for metric_name in metrics])

            y_avg = np.average(y, axis=1)
            y_std = np.std(y, axis=1)

            marker = random.choice(self.MARKERS)
            color = random.choice(self.COLORS)
            for i in range(len(x)):
                avg_point = ax.plot(x,
                                    y_avg,
                                    marker=marker,
                                    color=color,
                                    label=metric_name,
                                    markersize=markersize,
                                    linewidth=linewidth
                                    )
                if kwargs.pop('traj_point', True):
                    traj_point = plt.subplot().scatter([x] * y.shape[1],
                                                       y,
                                                       marker=marker,
                                                       color=color
                                                       )
                if kwargs.pop('traj_fill', True):
                    traj_fill = plt.subplot().fill_between(x,
                                                           y_avg - y_std,
                                                           y_avg + y_std,
                                                           color=color,
                                                           hatch=hatches[i] if hatches else None,
                                                           alpha=alpha
                                                           )

            legend_without_duplicate_labels(ax)

            tex_xtick = list(metrics.keys()) if xticks is None else xticks

        plt.xlabel(xlabel if xlabel else 'Difference Param in Trails')
        plt.ylabel(' and '.join(list(self.metrics.keys())))

        plt.grid()
        plt.minorticks_on()

        plt.xticks(list(range(len(metrics.keys()))), fontsize=fontsize)
        plt.yticks(fontsize=fontsize, rotation=rotation)

        if not save_path:
            plt.show()
        else:
            try:
                tikz_code = tikzplotlib.get_tikz_code()
            except ValueError as e:
                self.traj_plot(save_path, **kwargs)

            tex_src = self.traj_plot_tex_template.replace('$tikz_code$', tikz_code)

            tex_src = tex_src.replace('$xticklabel$', ','.join(tex_xtick))
            tex_src = tex_src.replace('$xtick$', ','.join([str(x) for x in range(len(tex_xtick))]))
            tex_src = tex_src.replace('$xlabel$', xlabel)
            tex_src = tex_src.replace('$ylabel$', ylabel)
            tex_src = fix_tex_traj_plot_legend(tex_src, self.metrics)

            # plt.savefig(save_path, dpi=1000, format='pdf')
            fout = open((save_path + '_metric_traj_plot.tex').lstrip('_'), mode='w', encoding='utf8')
            fout.write(tex_src)
            fout.close()
            texs = find_cwd_files('.tex')
            for pdf in texs:
                cmd = 'pdflatex "{}" '.format(pdf).replace(os.path.sep, '/')
                subprocess.check_call(shlex.split(cmd), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                # os.system(cmd)

            pdfs = find_cwd_files('.pdf', exclude_key='crop')
            for pdf in pdfs:
                cmd = 'pdfcrop "{}" "{}" '.format(pdf, pdf).replace(os.path.sep, '/')
                subprocess.check_call(shlex.split(cmd), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                # os.system(cmd)

            for f in find_cwd_files(['.aux']) + find_cwd_files(['.log']) + find_cwd_files(['crop']):
                os.remove(f)
        print('Traj plot finished')
        plt.close()

    def box_plot(self, save_path=None, **kwargs):

        ax = plt.subplot()

        alpha = kwargs.pop('alpha', 1)

        markersize = kwargs.pop('markersize', 3)

        xlabel = kwargs.pop('xlabel', '')

        xticks = kwargs.pop('xticks', '')

        ylabel = kwargs.pop('ylabel', '')

        yticks = kwargs.pop('yticks', '')

        legend_loc = kwargs.pop('legend_loc', 2)

        hatches = kwargs.pop('hatches', None)

        fontsize = kwargs.pop('fontsize', 12)

        rotation = kwargs.pop('rotation', 0)

        linewidth = kwargs.pop('linewidth', 3)

        widths = kwargs.pop('widths', 0.5)

        box_parts = []
        legend_labels = []
        for metric_name in self.metrics.keys():
            color = random.choice(self.COLORS)
            metrics = self.metrics[metric_name]
            tex_xtick = list(metrics.keys()) if xticks is None else xticks

            data = [metrics[trail] for trail in metrics.keys()]

            boxs_parts = ax.boxplot(data, widths=widths, meanline=True)

            box_parts.append(boxs_parts['boxes'][0])
            legend_labels.append(metric_name)

            plt.xlabel(xlabel if xlabel else 'Difference Param in Trails')
            plt.ylabel(' and '.join(list(self.metrics.keys())))

            for item in ['boxes', 'whiskers', 'fliers', 'medians', 'caps']:
                plt.setp(boxs_parts[item], color=color)

            plt.setp(boxs_parts["fliers"], markeredgecolor=color)

        plt.grid()
        plt.minorticks_on()

        plt.legend(box_parts, legend_labels, loc=legend_loc)

        if not save_path:
            plt.show()
        else:
            try:
                tikz_code = tikzplotlib.get_tikz_code()
            except ValueError as e:
                self.box_plot(save_path, **kwargs)

            tex_src = self.box_plot_tex_template.replace('$tikz_code$', tikz_code)

            tex_src = tex_src.replace('$xticklabel$', ','.join([str(x) for x in tex_xtick]))
            tex_src = tex_src.replace('$xtick$', ','.join([str(x + 1) for x in range(len(tex_xtick))]))
            tex_src = tex_src.replace('$xlabel$', xlabel)
            tex_src = tex_src.replace('$ylabel$', ylabel)

            # plt.savefig(save_path, dpi=1000, format='pdf')
            fout = open((save_path + '_metric_box_plot.tex').lstrip('_'), mode='w', encoding='utf8')
            fout.write(tex_src)
            fout.close()
            texs = find_cwd_files('.tex')
            for pdf in texs:
                cmd = 'pdflatex "{}" '.format(pdf).replace(os.path.sep, '/')
                subprocess.check_call(shlex.split(cmd), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                # os.system(cmd)

            pdfs = find_cwd_files('.pdf', exclude_key='crop')
            for pdf in pdfs:
                cmd = 'pdfcrop "{}" "{}" '.format(pdf, pdf).replace(os.path.sep, '/')
                subprocess.check_call(shlex.split(cmd), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                # os.system(cmd)

            for f in find_cwd_files(['.aux']) + find_cwd_files(['.log']) + find_cwd_files(['crop']):
                os.remove(f)

        print('Box plot finished')
        plt.close()

    def violin_plot(self, save_path=None, **kwargs):

        legend_labels = []

        def add_label(violin, label):
            color = violin["bodies"][0].get_facecolor().flatten()
            legend_labels.append((mpatches.Patch(color=color), label))

        ax = plt.subplot()

        alpha = kwargs.pop('alpha', 1)

        markersize = kwargs.pop('markersize', 3)

        xlabel = kwargs.pop('xlabel', '')

        xticks = kwargs.pop('xticks', '')

        ylabel = kwargs.pop('ylabel', '')

        yticks = kwargs.pop('yticks', '')

        legend_loc = kwargs.pop('legend_loc', 2)

        hatches = kwargs.pop('hatches', None)

        fontsize = kwargs.pop('fontsize', 12)

        rotation = kwargs.pop('rotation', 0)

        linewidth = kwargs.pop('linewidth', 3)

        violin_parts = []
        legend_labels = []
        for metric_name in self.metrics.keys():
            metric = self.metrics[metric_name]
            tex_xtick = list(metric.keys()) if xticks is None else xticks

            data = [metric[trail] for trail in metric.keys()]

            violin = ax.violinplot(data, showmeans=True, showmedians=True, showextrema=True)

            plt.xlabel(xlabel if xlabel else 'Difference Param in Trails')
            plt.ylabel(' and '.join(list(self.metrics.keys())))

            for pc in violin['bodies']:
                pc.set_linewidth(linewidth)

            violin_parts.append(violin["bodies"][0])
            legend_labels.append(metric_name)

        plt.grid()
        plt.minorticks_on()

        plt.legend(violin_parts, legend_labels, loc=legend_loc)

        if not save_path:
            plt.show()
        else:
            try:
                tikz_code = tikzplotlib.get_tikz_code()
            except ValueError as e:
                self.violin_plot(save_path, **kwargs)

            tex_src = self.box_plot_tex_template.replace('$tikz_code$', tikz_code)

            tex_src = tex_src.replace('$xticklabel$', ','.join([str(x) for x in tex_xtick]))
            tex_src = tex_src.replace('$xtick$', ','.join([str(x + 1) for x in range(len(tex_xtick))]))
            tex_src = tex_src.replace('$xlabel$', xlabel)
            tex_src = tex_src.replace('$ylabel$', ylabel)

            # plt.savefig(save_path, dpi=1000, format='pdf')
            fout = open((save_path + '_metric_violin_plot.tex').lstrip('_'), mode='w', encoding='utf8')
            fout.write(tex_src)
            fout.close()
            texs = find_cwd_files('.tex')
            for pdf in texs:
                cmd = 'pdflatex "{}"'.format(pdf).replace(os.path.sep, '/')
                subprocess.check_call(shlex.split(cmd), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                # os.system(cmd)

            pdfs = find_cwd_files('.pdf', exclude_key='crop')
            for pdf in pdfs:
                cmd = 'pdfcrop "{}" "{}"'.format(pdf, pdf).replace(os.path.sep, '/')
                subprocess.check_call(shlex.split(cmd), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                # os.system(cmd)

            for f in find_cwd_files(['.aux']) + find_cwd_files(['.log']) + find_cwd_files(['crop']):
                os.remove(f)

        print('Violin plot finished')

        plt.close()

    def summary(self, save_path=None, **kwargs):
        summary_str = ' -------------------- Metric Summary --------------------\n'
        header = ['Metric', 'Trail', 'Values', 'Summary']

        table_data = []

        for mn in self.metrics.keys():
            metrics = self.metrics[mn]
            for trail in metrics.keys():
                _data = []
                _data += [[mn, trail, metrics[trail]]]
                _data[-1].append(
                    ['Avg:{}, Median: {}, IQR: {}, Max: {}, Min: {}'.format(
                        round(np.average(metrics[trail]), 2),
                        round(np.median(metrics[trail]), 2),
                        round(iqr(metrics[trail], rng=(25, 75), interpolation='midpoint'), 2),
                        round(np.max(metrics[trail]), 2),
                        round(np.min(metrics[trail]), 2)
                    )]
                )
                table_data += _data

        summary_str += tabulate(table_data,
                                headers=header,
                                numalign='center',
                                tablefmt='fancy_grid')
        summary_str += '\n -------------------- Metric Summary --------------------\n'

        print(summary_str)

        if save_path:
            fout = open(save_path + '_summary.txt', mode='w', encoding='utf8')
            summary_str += '\n{}\n'.format(str(self.metrics))
            fout.write(summary_str)
            fout.close()
