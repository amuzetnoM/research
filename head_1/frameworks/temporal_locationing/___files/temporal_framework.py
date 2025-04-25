"""
Temporal Framework Module

This module provides the Temporal Framework, which is designed to handle time-related awareness for the AI. 
It acts as a wrapper for the core functionalities provided by the temporal_core module.

The framework provides a high-level interface for interacting with time, allowing the AI to understand 
and reason about temporal information.

"""

from head_1.frameworks.temporal_locationing.___files.temporal_core import TemporalCore
from head_1.frameworks.temporal_locationing.___files.temporal_api import TemporalAPI


class TemporalFramework:
    """
    TemporalFramework Class

    This class serves as the main interface for interacting with the Temporal Framework. 
    It utilizes the TemporalCore for underlying time-related operations and provides 
    methods to get the current time, understand the impact of past actions on the future, 
    handle time units, and anticipate future events.

    """

    def __init__(self):
        """
        Initializes the TemporalFramework.

        Creates instances of TemporalCore and TemporalAPI to handle the framework's operations.
        """
        self.temporal_core = TemporalCore()
        self.temporal_api = TemporalAPI(self.temporal_core)

    def get_current_time(self):
        """
        Gets the current time.

        Returns:
            datetime: The current time.
        """
        return self.temporal_api.get_current_time()

    def get_time_units(self):
        """
        Get supported time units.

        Returns:
            list: list of supported time units.
        """
        return self.temporal_api.get_time_units()

    def understand_past_action_impact(self, action, timestamp):
        """
        Analyzes how a past action might impact the future.

        Args:
            action (str): The past action to analyze.
            timestamp (datetime): The timestamp of when the action occurred.

        Returns:
            str: An analysis of the potential future impact of the action.
        """
        return self.temporal_api.understand_past_action_impact(action, timestamp)

    def anticipate_future(self, events):
        """
        Predicts future events based on current information.

        Args:
            events (list): A list of events to consider.

        Returns:
            str: A prediction of future events.
        """
        return self.temporal_api.anticipate_future(events)