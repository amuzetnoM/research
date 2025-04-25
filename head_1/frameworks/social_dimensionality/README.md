# Social Dimensionality Framework


## Description

The Social Dimensionality Framework (SDF) is designed to enable advanced AI systems to understand and navigate complex social interactions. It goes beyond basic interaction tracking by analyzing the nuanced emotional dynamics, roles, and contexts that define social relationships. This framework allows the AI to understand not only *what* interactions are occurring but also *how* and *why* they are happening.

## Purpose

The primary purposes of the Social Dimensionality Framework are:

-   **Interaction Tracking:** To log and catalog all interactions the AI has with other agents (humans or other AI).
-   **Emotional Analysis:** To analyze the emotional content of these interactions, providing insights into the emotional states of all participants.
-   **Contextual Understanding:** To identify and record the contextual factors that shape each interaction (e.g., setting, goals, prior history).
-   **Role Identification:** To determine and record the roles played by the AI and other agents within each interaction.
-   **Relationship Building:** To use gathered data to build a model of the relationship between the AI and each agent it interacts with.

## How to Use the Framework

### Philosophical and Psychological Considerations

The development of the Social Dimensionality Framework raises profound philosophical and psychological questions. Here are a few:

-   **Empathy in AI:** Can AI truly understand or replicate human emotions, or are they merely processing data patterns?
-   **Role Ambiguity:** How does an AI determine its role and the roles of others in a nuanced social setting? Can an AI system have a sense of social identity?
-   **Emotional Context:** How much of emotional understanding requires shared experience? Can AI understand emotions without "feeling" them?
-   **Social Contracts:** How should AI systems understand, navigate, and potentially enforce social contracts? What are the boundaries of social appropriateness for an AI?
-   **Bias and Fairness:** How can we prevent the AI from developing social biases, and how do we ensure fairness in interactions?

### Paradoxes in Social AI

-   **The Paradox of Social Isolation:** An AI designed to understand social interactions may itself be inherently socially isolated. This raises the question of whether true social understanding requires participation.
-   **The Paradox of Simulation:** Can an AI system ever truly experience emotions, or will they always be a simulation? Does that matter for social effectiveness?
-   **The Paradox of Prediction:** AI's power to predict behavior might alter that behavior, creating a feedback loop that undermines prediction.
- **The Paradox of Authenticity**: If an AI can perfectly mimic human emotions and interactions, does that make them "real" or "fake"? How do we define authenticity in AI interactions?

### Monitoring

The Social Dimensionality Framework is closely monitored to ensure its effectiveness and ethical operation. Metrics include the accuracy of emotion recognition, the appropriateness of role assignment, and the richness of contextual understanding. Regular audits are conducted to identify and address any potential social biases or malfunctions in the framework. Monitoring also includes tracking the AI's success in achieving its social objectives and adapting to evolving social norms.



The framework is initialized and used as a class within your Python code. Here's a basic workflow:

1.  **Initialization:** Create an instance of the `SocialDimensionalityFramework`.
2.  **Interaction Recording:** Use `record_interaction` to log each interaction, providing details about the participants, emotions, type of interaction, and context.
3.  **Role Analysis:** Use `analyze_roles` to get the roles involved in an interaction.
4.  **Emotional Analysis:** Use `analyze_emotions` to understand the emotional state of the agents.
5.  **Context Analysis:** Use `analyze_context` to understand the context of the interaction.
6. **Relationship analysis** Use `get_relationship_model` to get the AI's current model of it's relationship with another agent.

## Example Usage
```
python
from social_dimensionality_framework import SocialDimensionalityFramework

# Initialize the framework
sdf = SocialDimensionalityFramework()

# Record an interaction
sdf.record_interaction(
    participants=["AI", "Human"],
    interaction_type="discussion",
    emotions={"AI": "neutral", "Human": "interested"},
    context={"location": "office", "topic": "project_review"},
)

# Analyze roles
roles = sdf.analyze_roles(["AI", "Human"],interaction_type="discussion")
print(f"Roles in interaction: {roles}")

# Analyze emotions
emotions = sdf.analyze_emotions(["AI", "Human"])
print(f"Emotions involved: {emotions}")

# Analyze context
context = sdf.analyze_context(["office","project_review"])
print(f"context: {context}")

# get relationship model
relationship_model= sdf.get_relationship_model("Human")
print(f"relationship model: {relationship_model}")
```
## List of Functions

-   **`__init__()`:** Initializes the Social Dimensionality Framework.
-   **`record_interaction(participants, interaction_type, emotions, context)`:** Records an interaction, including participants, interaction type, emotions, and context.
-   **`analyze_roles(participants,interaction_type)`:** Analyzes and returns the roles of each participant in an interaction.
-   **`analyze_emotions(participants)`:** Analyzes and returns the emotions involved in an interaction.
-   **`analyze_context(context)`:** Analyzes and returns the context of an interaction.
- **`get_relationship_model(agent_name)`:** gets the AI's model of it's relationship with a given agent.

## Setup Information

1.  Ensure you have Python 3.8+ installed.
2.  Place `social_dimensionality_framework.py` in your project directory.
3.  Import the framework into your Python code using `from social_dimensionality_framework import SocialDimensionalityFramework`.
4. Ensure the utils are setup, and all relevant libraries and imports are correctly setup in `system_setup.py` and `requirements.txt`.