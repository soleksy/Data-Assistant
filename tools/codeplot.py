import os
import uuid

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class PlotGeneratorInput(BaseModel):
    code: str = Field(..., description="The code to generate the plot")

class PlotGeneratorTool(BaseTool):
    name = "plot_generator"
    description = "A Python shell to create plots using matplotlib. Use this to execute python commands when planning to generate plots using matplotlib."
    args_schema: Type[BaseModel] = PlotGeneratorInput

    def _run(self, code: str) -> str:

        project_root_dir = os.path.dirname(os.path.dirname(__file__))
        files_dir = os.path.join(project_root_dir, 'files')
        plots_dir = os.path.join(project_root_dir, 'plots')
        file_path = os.path.join(files_dir, st.session_state['file_name'])

        df = pd.read_csv(file_path, low_memory=False)
        try:
            namespace = {'df' : df , 'plt': plt}
            exec(code, namespace)

            if 'plt' in namespace:
                plt_ = namespace['plt']
                unique_id = uuid.uuid4()
                file_name = f"{unique_id}.png"

                plot_path = os.path.join(plots_dir, file_name)
                plt_.savefig(plot_path)
                plt_.close()
                return unique_id
            else:
                return "No plot object found in the provided code."

        except Exception as e:
            return f"Error generating plot: {str(e)}"

    async def _arun(self, code: str, file_name: str) -> str:
        return self._run(code, file_name)