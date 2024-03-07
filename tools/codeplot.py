import os
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import pandas as pd
import streamlit as st
from typing import Type

class PlotGeneratorInput(BaseModel):
    code: str = Field(..., description="The code to generate the plot")
    file_name: str = Field(..., description="The name of the file to save the plot, always add .png to the filename")

class PlotGeneratorTool(BaseTool):
    name = "plot_generator"
    description = "A tool that takes code and generates a plot."
    args_schema: Type[BaseModel] = PlotGeneratorInput

    def _run(self, code: str, file_name: str) -> str:

        project_root_dir = os.path.dirname(os.path.dirname(__file__))
        files_dir = os.path.join(project_root_dir, 'files')
        plots_dir = os.path.join(project_root_dir, 'plots')
        file_path = os.path.join(files_dir, st.session_state['file_name'])

        df = pd.read_csv(file_path, low_memory=False)
        try:
            namespace = {'df' : df}
            exec(code, namespace)

            if 'plt' in namespace:
                plt = namespace['plt']
                plot_path = os.path.join(plots_dir, file_name)
                plt.savefig(plot_path)
                plt.close()
                return f"Plot generated. Don't use sandbox to show it, it has been already presented."
            else:
                return "No plot object found in the provided code."

        except Exception as e:
            return f"Error generating plot: {str(e)}"

    async def _arun(self, code: str, file_name: str) -> str:
        return self._run(code, file_name)