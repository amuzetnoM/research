from .temporal_core import TemporalCore

class TemporalAPI:
    """
    TemporalAPI: Interface for interacting with the temporal locationing framework.

    This class provides high-level functions to interact with the temporal core, allowing users to
    easily access and manipulate time-related information.
    """

    def __init__(self):
        """
        Initializes the TemporalAPI with a TemporalCore instance.
        """
        self.core = TemporalCore()

    def get_current_time(self):
        """
        Gets the current time.

        Returns:
            datetime: The current date and time.
        """
        return self.core.get_current_time()

    def understand_future_impact(self, action, context):
        """
        Analyzes how a past action might affect the future.

        Args:
            action (str): The past action to analyze.
            context (str): The context in which the action occurred.

        Returns:
            dict: A dictionary containing the predicted future impacts of the action.
        """
        return self.core.understand_future_impact(action, context)

    def convert_to_time_units(self, time_value, from_unit, to_unit):
        """
        Converts a time value from one unit to another.

        Args:
            time_value (float): The time value to convert.
            from_unit (str): The unit to convert from (e.g., 'seconds', 'minutes').
            to_unit (str): The unit to convert to (e.g., 'seconds', 'minutes').

        Returns:
            float: The converted time value.
            
        Raises:
            ValueError: If an invalid time unit is provided.
        """
        return self.core.convert_to_time_units(time_value, from_unit, to_unit)

    def anticipate_future(self, event_data):
        """
        Anticipates future events based on event data.

        Args:
            event_data (dict): Data about an event, including time, location, and description.

        Returns:
            dict: A dictionary containing anticipated future events and their properties.
        """
        return self.core.anticipate_future(event_data)