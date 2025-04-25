"""
This module defines the Social API, providing an interface for interacting with
the core social logic and managing social interactions.

The Social API acts as a bridge between the Social Dimensionality Framework
and the core social functionalities, allowing higher-level components to
access and manipulate social data.
"""

from typing import List, Dict, Tuple
from .social_core import SocialCore


class SocialAPI:
    """
    The SocialAPI class provides methods to interact with the social core.
    It manages social interactions, tracks emotions, participants, and context.

    Attributes:
        social_core (SocialCore): An instance of the SocialCore class.
    """

    def __init__(self):
        """
        Initializes the SocialAPI with an instance of SocialCore.
        """
        self.social_core = SocialCore()

    def register_interaction(self, interaction_type: str, emotions: Dict[str, float],
                             participants: List[str], context: str) -> None:
        """
        Registers a new interaction with the social core.

        Args:
            interaction_type (str): The type of the interaction.
            emotions (Dict[str, float]): A dictionary of emotions and their intensities.
            participants (List[str]): A list of participants involved in the interaction.
            context (str): The context of the interaction.
        """
        self.social_core.register_interaction(interaction_type, emotions, participants, context)

    def get_interactions(self) -> List[Dict]:
        """
        Retrieves all registered interactions.

        Returns:
            List[Dict]: A list of dictionaries, each representing an interaction.
        """
        return self.social_core.get_interactions()

    def get_interaction_details(self, interaction_id: int) -> Dict:
        """
        Retrieves the details of a specific interaction.

        Args:
            interaction_id (int): The ID of the interaction.

        Returns:
            Dict: A dictionary containing the details of the interaction.
        """
        return self.social_core.get_interaction_details(interaction_id)

    def analyze_emotions(self, text: str) -> Dict[str, float]:
        """
        Analyzes the emotions in a given text.

        Args:
            text (str): The text to analyze.

        Returns:
            Dict[str, float]: A dictionary of emotions and their intensities.
        """
        return self.social_core.analyze_emotions(text)

    def get_participants_in_interaction(self, interaction_id: int) -> List[str]:
        """
        Gets a list of participants involved in a specific interaction.

        Args:
            interaction_id (int): The ID of the interaction.

        Returns:
            List[str]: A list of participant names.
        """
        return self.social_core.get_participants_in_interaction(interaction_id)

    def get_context_of_interaction(self, interaction_id: int) -> str:
        """
        Gets the context of a specific interaction.

        Args:
            interaction_id (int): The ID of the interaction.

        Returns:
            str: The context of the interaction.
        """
        return self.social_core.get_context_of_interaction(interaction_id)

    def get_interaction_type(self, interaction_id: int) -> str:
        """
        Gets the type of a specific interaction.

        Args:
            interaction_id (int): The ID of the interaction.

        Returns:
            str: The type of the interaction.
        """
        return self.social_core.get_interaction_type(interaction_id)

    def determine_role(self, agent_id: str, interaction_id: int) -> str:
        """
        Determines the role of an agent in a specific interaction.

        Args:
            agent_id (str): The ID of the agent.
            interaction_id (int): The ID of the interaction.

        Returns:
            str: The role of the agent in the interaction.
        """
        return self.social_core.determine_role(agent_id, interaction_id)

    def get_agent_roles(self, interaction_id: int) -> Dict[str, str]:
        """
        Gets the roles of all agents in a specific interaction.

        Args:
            interaction_id (int): The ID of the interaction.

        Returns:
            Dict[str, str]: A dictionary of agent IDs and their roles.
        """
        return self.social_core.get_agent_roles(interaction_id)
    
    def get_emotion_in_interaction(self, interaction_id: int) -> Dict[str, float]:
        """
        Gets the emotions present in a specific interaction.

        Args:
            interaction_id (int): The ID of the interaction.

        Returns:
            Dict[str, float]: A dictionary of emotions and their intensities.
        """
        return self.social_core.get_emotion_in_interaction(interaction_id)