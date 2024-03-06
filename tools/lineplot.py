import os

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from langchain.tools import BaseTool
from pydantic import BaseModel

from typing import Type, List, Optional

class LineSeries(BaseModel):
    x_column_name: str
    y_column_name: str
    label: Optional[str] = None
    color: Optional[str] = None
    linestyle: Optional[str] = None
    marker: Optional[str] = None

class LinePlotSchema(BaseModel):
    filename: str
    series: List[LineSeries]
    plot_title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    legend: Optional[bool] = True

class LinePlot(BaseTool):
    name = "line_plot"
    description = "Creates a flexible line plot given multiple series and customization options. Always add .png to the filename."
    args_schema: Type[BaseModel] = LinePlotSchema

    def _plot_series(self, ax, line_series: LineSeries, df: pd.DataFrame):
        ax.plot(df[line_series.x_column_name], df[line_series.y_column_name], label=line_series.label,
                color=line_series.color, linestyle=line_series.linestyle, marker=line_series.marker)

    def _run(self, filename: str, series: List[LineSeries], plot_title: str = '', x_label: str = '', y_label: str = '', legend: bool = True) -> str:
        project_root_dir = os.path.dirname(os.path.dirname(__file__))
        files_dir = os.path.join(project_root_dir, 'files')
        plots_dir = os.path.join(project_root_dir, 'plots')
        file_path = os.path.join(files_dir, st.session_state['file_name'])

        df = pd.read_csv(file_path, low_memory=False)
        fig, ax = plt.subplots()

        for series_config in series:
            self._plot_series(ax, series_config, df)

        if plot_title:
            ax.set_title(plot_title)
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)
        if legend:
            ax.legend()

        plot_path = os.path.join(plots_dir, filename)
        fig.savefig(plot_path)
        plt.close(fig)

        return plot_path
    
    async def _arun(self, filename: str, series: List[LineSeries], plot_title: str = '', x_label: str = '', y_label: str = '', legend: bool = True) -> str:
        return self._run(filename, series, plot_title, x_label, y_label, legend)