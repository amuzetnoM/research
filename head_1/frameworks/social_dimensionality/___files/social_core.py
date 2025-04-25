# -*- coding: utf-8 -*-
"""
Social Core Module

This module provides the core functionalities for managing and analyzing social
interactions within the AI system. It handles tracking, analyzing, and
understanding interactions between the AI and other agents.

"""

from datetime import datetime
from typing import List, Dict, Any


class SocialInteraction:
    """
    Represents a social interaction between the AI and other agents.

    Attributes:
        timestamp (datetime): The timestamp of the interaction.
        interaction_type (str): The type of interaction (e.g., "conversation", "collaboration", "conflict").
        emotions (Dict[str, float]): A dictionary of emotions involved in the interaction and their intensities.
        participants (List[str]): The list of agents involved in the interaction.
        context (Dict[str, Any]): Additional contextual information about the interaction.
        roles (Dict[str, str]): The roles of each agent in the interaction.
    """

    def __init__(self, interaction_type: str, participants: List[str], context: Dict[str, Any] = None):
        """
        Initializes a SocialInteraction instance.

        Args:
            interaction_type (str): The type of interaction.
            participants (List[str]): The agents involved in the interaction.
            context (Dict[str, Any], optional): Contextual information. Defaults to None.
        """
        self.timestamp: datetime = datetime.now()
        self.interaction_type: str = interaction_type
        self.emotions: Dict[str, float] = {}
        self.participants: List[str] = participants
        self.context: Dict[str, Any] = context if context is not None else {}
        self.roles: Dict[str, str] = {}

    def add_emotion(self, emotion: str, intensity: float):
        """
        Adds an emotion to the interaction with its intensity.

        Args:
            emotion (str): The name of the emotion.
            intensity (float): The intensity of the emotion.
        """
        self.emotions[emotion] = intensity

    def set_role(self, agent: str, role: str):
        """
        Sets the role of an agent in the interaction.

        Args:
            agent (str): The name of the agent.
            role (str): The role of the agent.
        """
        self.roles[agent] = role


class SocialCore:
    """
    Manages and analyzes social interactions.

    Attributes:
        interactions (List[SocialInteraction]): A list of recorded social interactions.
    """

    def __init__(self):
        """Initializes the SocialCore."""
        self.interactions: List[SocialInteraction] = []

    def record_interaction(self, interaction_type: str, participants: List[str], context: Dict[str, Any] = None) -> SocialInteraction:
        """
        Records a new social interaction.

        Args:
            interaction_type (str): The type of interaction.
            participants (List[str]): The agents involved in the interaction.
            context (Dict[str, Any], optional): Contextual information. Defaults to None.

        Returns:
            SocialInteraction: The newly recorded interaction.
        """
        interaction = SocialInteraction(interaction_type, participants, context)
        self.interactions.append(interaction)
        return interaction

    def analyze_emotions(self, interaction: SocialInteraction) -> Dict[str, float]:
        """
        Analyzes the emotions involved in a social interaction.

        Args:
            interaction (SocialInteraction): The interaction to analyze.

        Returns:
            Dict[str, float]: A dictionary of emotions and their intensities.
        """
        return interaction.emotions

    def identify_participants(self, interaction: SocialInteraction) -> List[str]:
        """
        Identifies the participants in a social interaction.

        Args:
            interaction (SocialInteraction): The interaction to analyze.

        Returns:
            List[str]: The list of participants.
        """
        return interaction.participants

    def understand_context(self, interaction: SocialInteraction) -> Dict[str, Any]:
        """
        Understands the context of a social interaction.

        Args:
            interaction (SocialInteraction): The interaction to analyze.

        Returns:
            Dict[str, Any]: The contextual information.
        """
        return interaction.context

    def determine_roles(self, interaction: SocialInteraction) -> Dict[str, str]:
        """
        Determines the roles of each participant in the interaction.

        Args:
            interaction (SocialInteraction): The interaction to analyze.

        Returns:
            Dict[str, str]: The roles of each participant.
        """
        return interaction.roles

    def get_interactions_by_type(self, interaction_type: str) -> List[SocialInteraction]:
        """
        Retrieves interactions of a specific type.

        Args:
            interaction_type (str): The type of interactions to retrieve.

        Returns:
            List[SocialInteraction]: A list of interactions of the specified type.
        """
        return [interaction for interaction in self.interactions if interaction.interaction_type == interaction_type]

    def get_interactions_with_agent(self, agent: str) -> List[SocialInteraction]:
        """
        Retrieves interactions involving a specific agent.

        Args:
            agent (str): The agent to find interactions with.

        Returns:
            List[SocialInteraction]: A list of interactions involving the specified agent.
        """
        return [interaction for interaction in self.interactions if agent in interaction.participants]