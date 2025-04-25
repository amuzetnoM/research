"""
Social Dimensionality Framework

This module provides a high-level interface for interacting with the core social
dimensionality functionality. It wraps the core logic, making it easier to use
and integrate into other parts of the system.

Classes:
    SocialFramework: A wrapper class for interacting with the social
                     dimensionality framework.

"""

from .social_core import SocialCore
from .social_api import SocialAPI


class SocialFramework:
    """
    A wrapper class for interacting with the social dimensionality framework.

    This class provides a simplified interface for using the core social
    analysis functionalities. It encapsulates the SocialCore and SocialAPI
    components, providing a cohesive and easy-to-use interface.

    Attributes:
        core (SocialCore): An instance of the SocialCore class.
        api (SocialAPI): An instance of the SocialAPI class.
    """

    def __init__(self):
        """
        Initializes the SocialFramework.

        Creates instances of SocialCore and SocialAPI, which are used to
        perform social dimensionality analysis and manage interactions.
        """
        self.core = SocialCore()
        self.api = SocialAPI(self.core)

    def track_interaction(self, interaction_type, emotions, participants, context):
        """
        Tracks a social interaction.

        Args:
            interaction_type (str): The type of interaction (e.g., "discussion", "collaboration").
            emotions (dict): A dictionary of emotions involved in the interaction.
            participants (list): A list of participants in the interaction.
            context (str): The context of the interaction.

        Returns:
            dict: The record of the tracked interaction.
        """
        return self.api.track_interaction(interaction_type, emotions, participants, context)

    def analyze_interaction(self, interaction_id):
        """
        Analyzes a specific interaction.

        Args:
            interaction_id (str): The ID of the interaction to analyze.

        Returns:
            dict: The analysis of the interaction.
        """
        return self.api.analyze_interaction(interaction_id)

    def get_all_interactions(self):
        """
        Retrieves all recorded interactions.

        Returns:
            list: A list of all recorded interactions.
        """
        return self.api.get_all_interactions()
    
    def determine_roles(self, interaction_id):
        """
        Determine the roles of participants in an interaction.

        Args:
            interaction_id (str): The ID of the interaction to analyze.
        Returns:
            dict: The determined roles of each participant.
        """
        return self.api.determine_roles(interaction_id)

    def get_participant_history(self, participant_id):
        """
        Retrieves the interaction history of a specific participant.

        Args:
            participant_id (str): The ID of the participant.

        Returns:
            list: A list of interactions involving the participant.
        """
        return self.api.get_participant_history(participant_id)