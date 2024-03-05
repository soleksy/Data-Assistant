import os
import streamlit as st

from langchain.tools import BaseTool

from pydantic import BaseModel
from typing import Type

class LinePlotSchema(BaseModel):
    filename: str
    x_column_name: str
    y_column_name: str
    plot_title: str


class LinePlot(BaseTool):
    name = "line_plot"
    description = "Creates a plot given column names X and Y. Always add .png to the end of filename."
    args_schema: Type[BaseModel] = LinePlotSchema

    def _run(self, filename: str, x_column_name: str, y_column_name: str, plot_title: str) -> str:
        import matplotlib.pyplot as plt
        import pandas as pd

        project_root_dir = os.path.dirname(os.path.dirname(__file__))

        files_dir = os.path.join(project_root_dir, 'files')
        plots_dir = os.path.join(project_root_dir, 'plots')

        file_path = os.path.join(files_dir, st.session_state['file_name'])

        df = pd.read_csv(file_path, low_memory=False)
        x_axis = df[x_column_name]
        y_axis = df[y_column_name]

        fig, ax = plt.subplots()
        ax.plot([x for x in x_axis], [y for y in y_axis])
        ax.set_title(plot_title)

        plot_path = os.path.join(plots_dir, filename)
        fig.savefig(plot_path)
        plt.close(fig)

        return plot_path
    
    async def _arun(self, filename: str, x_column_name: str, y_column_name:str, plot_title: str) -> str:
        import matplotlib.pyplot as plt
        import pandas as pd

        project_root_dir = os.path.dirname(os.path.dirname(__file__))


        files_dir = os.path.join(project_root_dir, 'files')
        plots_dir = os.path.join(project_root_dir, 'plots')

        file_path = os.path.join(files_dir, st.session_state['file_name'])

        df = pd.read_csv(file_path , low_memory=False)

        x_axis = df[x_column_name]
        y_axis = df[y_column_name]

        fig, ax = plt.subplots()
        ax.plot([x for x in x_axis], [y for y in y_axis])  
        ax.set_title(plot_title)

        plot_path = os.path.join(plots_dir, filename)
        fig.savefig(plot_path)
        plt.close(fig)