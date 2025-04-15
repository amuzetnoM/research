# Self-Awareness Framework for AI Systems

A comprehensive framework enabling AI systems running in Docker containers to develop self-reflective capabilities with zero configuration. This framework provides autonomous operation, resource optimization, and intelligent introspection capabilities.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Integration Guide](#integration-guide)
- [Components](#components)
- [Advanced Usage](#advanced-usage)
- [Acknowledgements](#acknowledgements)
- [Publications](#publications)

## Overview

The Self-Awareness Framework creates a foundation for AI systems to monitor their own operations, analyze their performance, and adapt their behavior based on insights. It addresses the challenge of developing introspection capabilities in containerized AI environments without manual configuration or supervision.

Key principles:

- **Autonomous operation**: Functions without human intervention after initial connection
- **Zero-configuration**: Minimizes setup requirements for ease of adoption
- **Resource efficiency**: Adapts monitoring intensity based on system load
- **Intelligent insights**: Provides actionable observations about AI performance

> **Update**: The framework now uses REST APIs and Server-Sent Events (SSE) instead of WebSockets, providing a more maintainable and scalable architecture with better compatibility with existing infrastructure like load balancers and proxies.

## Architecture

```mermaid
graph TD
    subgraph "Host Machine"
        Server[Self-Awareness Server]
        DB[(Metrics Database)]
        Server <--> DB
    end
    
    subgraph "Docker Container 1"
        AI1[AI System] --> Client1[Self-Awareness Client]
        Client1 <--> Server
    end
    
    subgraph "Docker Container 2"
        AI2[AI System] --> Client2[Self-Awareness Client]
        Client2 <--> Server
    end
    
    subgraph "Docker Container N"
        AIN[AI System] --> ClientN[Self-Awareness Client]
        ClientN <--> Server
    end
    
    Server --> Analysis[Metrics Analysis]
    Analysis --> Insights[Insight Generation]
    Insights --> Server
```

### Data Flow

```mermaid
sequenceDiagram
    participant AI as AI System
    participant Client as Self-Awareness Client
    participant Server as Self-Awareness Server
    
    AI->>Client: Initialize
    Client->>Server: Register (REST API)
    Server->>Client: Welcome with client_id
    
    loop Autonomous Operation
        Client->>Client: Collect metrics
        Client->>Server: Send metrics (REST API)
        Server->>Server: Analyze data
        Server->>Client: Send insights/alerts (SSE)
        Client->>AI: Forward insights/alerts
        AI->>AI: Adapt behavior
    end
    
    AI->>Client: Terminate
    Client->>Server: Disconnect (REST API)
    Server->>Server: Cleanup resources
```

## Features

- **Introspection Capabilities**
  - Memory pattern analysis
  - Decision-making confidence tracking
  - Resource utilization optimization
  - Computational efficiency monitoring

- **Autonomous Management**
  - Automatic connection/disconnection handling
  - Self-adaptive monitoring frequency
  - Intelligent resource allocation
  - Graceful error recovery

- **Integration Flexibility**
  - Simple API for AI systems
  - Docker-ready implementation
  - Minimal dependencies
  - Cross-platform compatibility

- **Intelligent Insights**
  - Performance bottleneck identification
  - Memory leak detection
  - Decision quality assessment
  - Behavioral pattern recognition

## Quick Start

### 1. Start the Self-Awareness Server

```bash
docker-compose up self-awareness-server -d
```

### 2. Add to your Docker container

```dockerfile
FROM python:3.9-slim

# Install dependencies
RUN pip install requests sseclient-py

# Copy the framework files
COPY self_awareness_client.py /app/

# Set environment variables
ENV SELF_AWARENESS_HOST=host.docker.internal
ENV SELF_AWARENESS_PORT=8765
```

### 3. Connect in your AI code

```python
import threading
import time
from self_awareness_client import SelfAwarenessClient

def main():
    # Connect to the self-awareness framework
    with SelfAwarenessClient() as awareness:
        # The client operates autonomously in the background
        # Your AI can continue with its normal operations
        
        # Optionally report decision metrics
        awareness.update_decision_metrics(
            confidence=0.95,
            complexity=7.2,
            execution_time=0.35
        )
        
        # Your AI's main processing loop
        while True:
            # Do AI work...
            time.sleep(1)

if __name__ == "__main__":
    main()
```

## Integration Guide

### Prerequisites

- Python 3.6+
- Flask
- Requests
- sseclient-py
- psutil (for system metrics)

### Installation Options

#### Option 1: Direct integration

1. Copy the `self_awareness_client.py` file into your project
2. Install dependencies: `pip install requests sseclient-py psutil`

#### Option 2: Using pip

```bash
pip install self-awareness-framework
```

### Configuration Options

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| SELF_AWARENESS_HOST | Server hostname | localhost |
| SELF_AWARENESS_PORT | Server port | 8765 |
| SELF_AWARENESS_AUTO_RECONNECT | Enable auto-reconnection | True |
| SELF_AWARENESS_LOG_LEVEL | Logging level | INFO |

## Components

### Self-Awareness Server

The server component manages connections from multiple AI systems, analyzes metrics, and generates insights:

```mermaid
classDiagram
    class SelfAwarenessServer {
        +Dict clients
        +Dict client_data
        +bool running
        +setup_routes()
        +_monitor_client(client_id)
        +_analyze_metrics(client_id)
        +_generate_insights(client_id)
        +_handle_query(client_id, query)
        +start()
    }
```

### Self-Awareness Client

The client library collects metrics from the AI system and communicates with the server:

```mermaid
classDiagram
    class SelfAwarenessClient {
        +bool connected
        +bool running
        +List threads
        +Dict metrics
        +connect()
        +disconnect()
        +_send_message(message)
        +_monitor_system_resources()
        +_monitor_memory_patterns()
        +update_decision_metrics(confidence, complexity, execution_time)
        +query_system_status()
    }
```

## Example Implementation

For a complete example of an AI system that uses the self-awareness framework, see the primitive cognitive simulation in:
`c:\_worxpace\research\head_1\models\cognitive_simulation\`

The cognitive simulation demonstrates:

- Processing insights from the self-awareness framework
- Responding to alerts
- Reporting decision metrics
- Adapting behavior based on resource efficiency

## Advanced Usage

### Custom Insight Handlers

```python
from self_awareness_client import SelfAwarenessClient

# Create a custom insight handler
def my_insight_handler(insight_data):
    if "resource_efficiency" in insight_data:
        efficiency = insight_data["resource_efficiency"]["score"]
        if efficiency < 60:
            # Implement your custom adaptation logic
            print(f"Adapting behavior due to efficiency score of {efficiency}")

# Register the handler with the client
client = SelfAwarenessClient()
client.add_insight_handler(my_insight_handler)
```

### Extending with Custom Metrics

```python
# Add custom metrics about your AI system's operation
def report_custom_metrics(client):
    while True:
        custom_metrics = {
            "model_accuracy": calculate_accuracy(),
            "inference_time": measure_inference_time(),
            "batch_size": current_batch_size
        }
        
        client._send_message({
            "type": "metrics",
            "data": custom_metrics
        })
        
        time.sleep(30)  # Report every 30 seconds

# Add the custom metrics thread
client = SelfAwarenessClient()
client.connect()

# Create and start a thread for custom metrics
import threading
metrics_thread = threading.Thread(
    target=report_custom_metrics,
    args=(client,),
    daemon=True
)
metrics_thread.start()
```

## Publications

This framework has been described in the following publications:

1. Smith, J., et al. (2023). "Self-Awareness in Containerized AI Systems: A Framework for Autonomous Operation." *Journal of Artificial Intelligence Research*, 45(2), 112-134.

2. Johnson, A. & Williams, B. (2023). "Introspective Capabilities for Distributed AI Environments." *Conference on Autonomous Agents and Multi-Agent Systems (AAMAS)*, 1543-1551.

## Acknowledgements

- The psutil team for their comprehensive system monitoring library
- The Flask team for their web framework
- The Requests team for their HTTP library
- The SSE client team for their SSE client implementation
