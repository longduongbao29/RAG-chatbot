from langchain_core.tools import BaseTool
import pytz
from datetime import datetime

class DateTimeTool(BaseTool):
    name: str = "datetime_tool"
    description: str = "A tool to get the current date and time in a specified format."

    def _run(self, **args) -> str:
        """Get the current date and time in the specified format."""
        timezone = pytz.timezone("Asia/Bangkok")
        current_date_time = "Current date and time: " + datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
        return current_date_time
