# -*- coding: utf-8 -*-
# file: tex_utils.py
# time: 2:47 2022/12/30
# author: yangheng <hy345@exeter.ac.uk>
# github: https://github.com/yangheng95
# huggingface: https://huggingface.co/yangheng
# google scholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# Copyright (C) 2021. All Rights Reserved.
import os.path
import re
from itertools import zip_longest
from pathlib import Path
from typing import Union


def extract_table_and_style_from_tex(tex_src_or_file_path):
    """Extract tables from tex file.

    Args:
        tex_src_or_file_path (str): tex file path.

    Returns:
        list: list of tables.
    """
    import re

    if os.path.exists(tex_src_or_file_path):
        with open(tex_src_or_file_path, "r", encoding="utf8") as f:
            tex = f.read()
    else:
        tex = tex_src_or_file_path
    tables = re.findall(r"\\addplot.*?\[.*?};", tex, re.DOTALL)
    styles = [t.split("[")[1].split("]")[0] for t in tables]
    return [tables, styles]


def extract_x_label_from_tex(tex_src_or_file_path):
    """Extract x label from tex file.

    Args:
        tex_src_or_file_path (str): tex file path.

    Returns:
        list: list of x label.
    """
    import re

    if os.path.exists(tex_src_or_file_path):
        with open(tex_src_or_file_path, "r", encoding="utf8") as f:
            tex = f.read()
    else:
        tex = tex_src_or_file_path
    x_labels = re.findall(r"xlabel.*?},", tex, re.DOTALL)
    return x_labels[0] if x_labels else None


def extract_y_label_from_tex(tex_src_or_file_path):
    """Extract y label from tex file.

    Args:
        tex_src_or_file_path (str): tex file path.

    Returns:
        list: list of y label.
    """
    import re

    if os.path.exists(tex_src_or_file_path):
        with open(tex_src_or_file_path, "r") as f:
            tex = f.read()
    else:
        tex = tex_src_or_file_path
    y_labels = re.findall(r"ylabel.*?},", tex, re.DOTALL)
    return y_labels[0] if y_labels else None


def extract_x_tick_from_tex(tex_src_or_file_path):
    """Extract x tick from tex file.

    Args:
        tex_src_or_file_path (str): tex file path.

    Returns:
        list: list of x tick.
    """
    import re

    if os.path.exists(tex_src_or_file_path):
        with open(tex_src_or_file_path, "r") as f:
            tex = f.read()
    else:
        tex = tex_src_or_file_path
    x_ticks = re.findall(r"xtick.*?}", tex, re.DOTALL)
    return x_ticks


def extract_y_tick_from_tex(tex_src_or_file_path):
    """Extract y tick from tex file.

    Args:
        tex_src_or_file_path (str): tex file path.

    Returns:
        list: list of y tick.
    """
    import re

    if os.path.exists(tex_src_or_file_path):
        with open(tex_src_or_file_path, "r") as f:
            tex = f.read()
    else:
        tex = tex_src_or_file_path
    y_ticks = re.findall(r"ytick.*?}", tex, re.DOTALL)
    return y_ticks


def extract_legend_from_tex(tex_src_or_file_path):
    """Extract legend from tex file.

    Args:
        tex_src_or_file_path (str): tex file path.

    Returns:
        list: list of legend.
    """
    import re

    if os.path.exists(tex_src_or_file_path):
        with open(tex_src_or_file_path, "r") as f:
            tex = f.read()
    else:
        tex = tex_src_or_file_path
    legends = re.findall(r"\\addlegendentry.*?}", tex, re.DOTALL)
    if legends:
        for i, legend in enumerate(legends):
            legends[i] = legend.replace("\\addlegendentry{", "").replace("}", "")
    if not legends:
        legends = re.findall(r"legend entries.*?}", tex, re.DOTALL)
        if not legends:
            return []
        legends = re.findall(r"{.*?}", legends[0], re.DOTALL)[0][1:-1].split(",")
    return legends


def remove_legend_from_tex(tex_src_or_file_path):
    """Remove legend from tex file.

    Args:
        tex_src_or_file_path (str): tex file path.

    Returns:
        list: list of legend.
    """
    import re

    if os.path.exists(tex_src_or_file_path):
        with open(tex_src_or_file_path, "r") as f:
            tex = f.read()
    else:
        tex = tex_src_or_file_path
    legends = re.findall(r"\\addlegendentry.*?}", tex, re.DOTALL)
    if legends:
        for i, legend in enumerate(legends):
            tex = tex.replace(legend, "")
    if not legends:
        legends = re.findall("legend entries.*?},.*?\n", tex, re.DOTALL)
        if legends:
            for i, legend in enumerate(legends):
                tex = tex.replace(legend, "")
    return tex


def extract_style_from_tex(tex_src_or_file_path):
    """Extract style from tex file.

    Args:
        tex_src_or_file_path (str): tex file path.

    Returns:
        list: list of style.
    """
    import re

    if os.path.exists(tex_src_or_file_path):
        with open(tex_src_or_file_path, "r") as f:
            tex = f.read()
    else:
        tex = tex_src_or_file_path
    styles = re.findall(r"\\begin{axis.*?,.*?\]", tex, re.DOTALL)
    for i, style in enumerate(styles):
        if ",\n]" not in styles[i]:
            styles[i] = styles[i].replace("\n]", ",\n]")
    return styles[0]


def extract_color_from_tex(tex_src_or_file_path):
    """
    Extract color from tex file.

    """
    import re

    if os.path.exists(tex_src_or_file_path):
        with open(tex_src_or_file_path, "r") as f:
            tex = f.read()
    else:
        tex = tex_src_or_file_path
    colors = re.findall(r"\\definecolor{.*?}{RGB}{.*?}", tex, re.DOTALL)
    return colors


def preprocess_style(tex_src_or_file_path):
    """Preprocess style.

    Args:
        tex_src_or_file_path (str): tex file path.

    Returns:
        list: list of style.
    """
    import re

    if os.path.exists(tex_src_or_file_path):
        with open(tex_src_or_file_path, "r") as f:
            tex = f.read()
    else:
        tex = tex_src_or_file_path
    styles = re.findall(r"\\begin{axis.*?,.*?\]", tex, re.DOTALL)
    assert len(styles) == 1
    for i, style in enumerate(styles):
        while "\n " in styles[i]:
            styles[i] = styles[i].replace("\n ", "\n")
        while " \n" in styles[i]:
            styles[i] = styles[i].replace(" \n", "\n")
        while "\t" in styles[i]:
            styles[i] = styles[i].replace("\t", "")

        if ",\n]" not in styles[i]:
            styles[i] = styles[i].replace("\n]", ",\n]")
        tex = tex.replace(style, styles[i])
    return tex


def reformat_tikz_format_for_colalab(
    template: Union[str, Path],
    tex_src_to_format: Union[str, Path],
    output_path: Union[str, Path] = None,
    style_settings: dict = None,
    **kwargs
):
    """Reformat tikz format.

    Args:
        template (str): template, file or tex_text.
        tex_src_to_format (str): tex src to format, file or tex_text.
        output_path (Path): output path.
        style_settings (dict): style settings.

    Returns:
        str: formatted tex src.

    """
    _template = template[:]
    _template = preprocess_style(_template)
    tex_src_to_format = preprocess_style(tex_src_to_format)

    head = re.findall(r"\\begin{tikzpicture}", tex_src_to_format, re.DOTALL)[0]
    for color in extract_color_from_tex(tex_src_to_format):
        _template = _template.replace(head, head + "\n" + color + "\n")

    for new_legend, old_legend in zip_longest(
        extract_legend_from_tex(tex_src_to_format), extract_legend_from_tex(_template)
    ):
        if old_legend and new_legend:
            _template = _template.replace(old_legend, new_legend, 1)
        elif old_legend and not new_legend:
            _template = _template.replace(old_legend, "", 1)
            while ",," in _template:
                _template = _template.replace(",,", ",")
        else:
            style_settings["legend"] = new_legend

    tikz_plot_style = extract_style_from_tex(_template)
    for k, v in style_settings.items():
        _template = _template.replace(
            tikz_plot_style, tikz_plot_style.replace("]", "{}={},\n]".format(k, v)), 1
        )

    if kwargs.get("no_legend", False):
        _template = remove_legend_from_tex(_template)

    new_table_and_styles = extract_table_and_style_from_tex(tex_src_to_format)
    old_table_and_styles = extract_table_and_style_from_tex(_template)
    for i in range(max(len(new_table_and_styles[0]), len(old_table_and_styles[0]))):

        new_table, new_style = new_table_and_styles[0][i], new_table_and_styles[1][i]
        if i < len(old_table_and_styles[0]):
            old_table, old_style = (
                old_table_and_styles[0][i],
                old_table_and_styles[1][i],
            )
        else:
            old_table, old_style = "", ""
        if old_table and new_table:
            _template = _template.replace(old_table, new_table, 1)
            _template = _template.replace(old_style, new_style, 1)
        elif old_table and not new_table:
            _template = _template.replace(old_table, "", 1)
            _template = _template.replace(old_style, "", 1)
        elif not old_table and new_table:
            _template = _template.replace(
                extract_style_from_tex(_template),
                extract_style_from_tex(_template) + "\n" + new_table + "\n",
                1,
            )
            # _template = _template.replace(tikz_plot_style, tikz_plot_style+'\n'+new_table, 1)
        else:
            raise ValueError("old_table and new_table are both None.")

    new_x_label = extract_x_label_from_tex(tex_src_to_format)
    old_x_label = extract_x_label_from_tex(_template)
    if old_x_label and new_x_label:
        _template = _template.replace(old_x_label, new_x_label, 1)
    elif old_x_label and not new_x_label:
        _template = _template.replace(old_x_label, "", 1)
    elif new_x_label:
        style_settings["xlabel"] = new_x_label.replace("xlabel=", "").replace(
            ",", ""
        )  # replace not available, waiting for style setting

    new_y_label = extract_y_label_from_tex(tex_src_to_format)
    old_y_label = extract_y_label_from_tex(_template)
    if old_y_label and new_y_label:
        _template = _template.replace(old_y_label, new_y_label, 1)
    elif old_y_label and not new_y_label:
        _template = _template.replace(old_y_label, "", 1)
    elif new_y_label:
        style_settings["ylabel"] = new_y_label.replace("ylabel=", "").replace(
            ",", ""
        )  # replace not available, waiting for style setting

    if os.path.exists(tex_src_to_format):
        output_path = os.path.join(Path(tex_src_to_format), ".tex")

    with open(os.path.join(output_path), "w") as f:
        f.write(_template)
    os.system("pdflatex %s %s" % (output_path, output_path))
    os.system(
        "pdfcrop %s %s"
        % (output_path.replace(".tex", ".pdf"), output_path.replace(".tex", ".pdf"))
    )

    return _template