#!/usr/bin/env python3
"""
Advanced Visualization Utilities for Cognitive Framework

This module provides specialized visualization capabilities for analyzing
and presenting cognitive simulation data:
- Interactive visualizations
- 3D visualizations of cognitive states
- Comparative visualizations for multiple simulations
- Animation capabilities for evolving cognitive systems
- Export functions for high-quality publication-ready figures
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from datetime import datetime
from pathlib import Path
import glob
import matplotlib
from matplotlib.figure import Figure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cognitive-visualization")

# Try to import visualization libraries, but don't fail if they're not available
try:
    import matplotlib.pyplot as plt
    from matplotlib import animation
    from mpl_toolkits.mplot3d import Axes3D
    HAS_MATPLOTLIB = True
except ImportError:
    logger.warning("Matplotlib not available. Basic visualization capabilities will be limited.")
    HAS_MATPLOTLIB = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    logger.warning("Plotly not available. Interactive visualization capabilities will be limited.")
    HAS_PLOTLY = False

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    logger.warning("Seaborn not available. Advanced statistical visualization capabilities will be limited.")
    HAS_SEABORN = False

try:
    from IPython.display import display, HTML
    HAS_IPYTHON = True
except ImportError:
    logger.warning("IPython not available. Notebook visualization capabilities will be limited.")
    HAS_IPYTHON = False

# Default configuration
DEFAULT_CONFIG = {
    "default_figsize": (10, 6),
    "style": "default",  # Options: 'default', 'dark', 'light', 'scientific'
    "dpi": 100,
    "cmap": "viridis",
    "show_grid": True,
    "interactive": True,
    "animation_fps": 30,
    "output_dir": "visualization_output",
    "font_size": 10,
    "line_width": 1.5,
    "marker_size": 6,
    "export_format": "png",  # Options: 'png', 'svg', 'pdf'
    "export_dpi": 300,
    "color_palette": "tab10"
}

# ==========================================
# Utility Functions
# ==========================================

def configure_matplotlib_style(style: str = "default") -> None:
    """Configure matplotlib style for consistent visualizations.
    
    Args:
        style: Style name ('default', 'dark', 'light', 'scientific')
    """
    if not HAS_MATPLOTLIB:
        return
    
    if style == "default":
        plt.style.use('seaborn-v0_8-whitegrid')
    elif style == "dark":
        plt.style.use('dark_background')
    elif style == "light":
        plt.style.use('seaborn-v0_8-bright')
    elif style == "scientific":
        plt.style.use('seaborn-v0_8-paper')
    else:
        logger.warning(f"Unknown style: {style}. Using default.")
        plt.style.use('seaborn-v0_8-whitegrid')
    
    # Set font sizes
    matplotlib.rcParams.update({
        'font.size': DEFAULT_CONFIG["font_size"],
        'axes.titlesize': DEFAULT_CONFIG["font_size"] + 2,
        'axes.labelsize': DEFAULT_CONFIG["font_size"],
        'xtick.labelsize': DEFAULT_CONFIG["font_size"] - 1,
        'ytick.labelsize': DEFAULT_CONFIG["font_size"] - 1,
        'legend.fontsize': DEFAULT_CONFIG["font_size"] - 1,
        'figure.titlesize': DEFAULT_CONFIG["font_size"] + 4
    })

def load_simulation_data(simulation_id: str, log_directory: str = "simulation_logs") -> Dict[str, Any]:
    """Load data for a specific simulation.
    
    Args:
        simulation_id: ID of the simulation to load
        log_directory: Directory containing simulation logs
        
    Returns:
        Dictionary containing simulation data
    """
    final_path = os.path.join(log_directory, f"{simulation_id}_final.json")
    
    if not os.path.exists(final_path):
        logger.error(f"Simulation data not found: {final_path}")
        return {}
    
    try:
        with open(final_path, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Loaded simulation data for {simulation_id}")
        return data
    except Exception as e:
        logger.error(f"Failed to load simulation data: {e}")
        return {}

def get_latest_simulation_id(log_directory: str = "simulation_logs") -> Optional[str]:
    """Get the ID of the most recent simulation.
    
    Args:
        log_directory: Directory containing simulation logs
        
    Returns:
        Simulation ID or None if no simulations are found
    """
    if not os.path.exists(log_directory):
        return None
    
    files = [f for f in os.listdir(log_directory) if f.endswith('_final.json')]
    if not files:
        return None
    
    # Sort by modification time, newest first
    files.sort(key=lambda x: os.path.getmtime(os.path.join(log_directory, x)), reverse=True)
    
    # Extract simulation ID from filename
    latest_file = files[0]
    simulation_id = latest_file.replace('_final.json', '')
    
    return simulation_id

def get_all_simulation_ids(log_directory: str = "simulation_logs") -> List[str]:
    """Get IDs of all available simulations.
    
    Args:
        log_directory: Directory containing simulation logs
        
    Returns:
        List of simulation IDs
    """
    if not os.path.exists(log_directory):
        return []
    
    files = [f for f in os.listdir(log_directory) if f.endswith('_final.json')]
    if not files:
        return []
    
    # Sort by modification time, newest first
    files.sort(key=lambda x: os.path.getmtime(os.path.join(log_directory, x)), reverse=True)
    
    # Extract simulation IDs from filenames
    return [f.replace('_final.json', '') for f in files]

def convert_to_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """Convert simulation data to pandas DataFrame for analysis.
    
    Args:
        data: Simulation data dictionary
        
    Returns:
        DataFrame containing simulation data
    """
    if not data or "data" not in data:
        return pd.DataFrame()
    
    sim_data = data["data"]
    
    # Create a basic DataFrame with iterations
    if "iterations" not in sim_data or not sim_data["iterations"]:
        return pd.DataFrame()
    
    df = pd.DataFrame({"iteration": sim_data["iterations"]})
    
    # Add energy levels
    if "energy_levels" in sim_data and len(sim_data["energy_levels"]) == len(sim_data["iterations"]):
        df["energy_level"] = sim_data["energy_levels"]
    
    # Add environment data
    if "obstacles" in sim_data and len(sim_data["obstacles"]) == len(sim_data["iterations"]):
        df["obstacles"] = sim_data["obstacles"]
    if "rewards" in sim_data and len(sim_data["rewards"]) == len(sim_data["iterations"]):
        df["rewards"] = sim_data["rewards"]
    if "environment_conditions" in sim_data and len(sim_data["environment_conditions"]) == len(sim_data["iterations"]):
        df["environment_condition"] = sim_data["environment_conditions"]
    
    # Add performance metrics
    for metric, values in sim_data.get("performance_metrics", {}).items():
        if len(values) == len(sim_data["iterations"]):
            df[f"metric_{metric}"] = values
    
    # Add behavior weights
    for behavior, values in sim_data.get("behavior_weights", {}).items():
        if len(values) == len(sim_data["iterations"]):
            df[f"weight_{behavior}"] = values
    
    return df

def ensure_output_directory(output_dir: Optional[str] = None) -> str:
    """Ensure the output directory exists.
    
    Args:
        output_dir: Directory to ensure (default: from config)
        
    Returns:
        Path to the output directory
    """
    if output_dir is None:
        output_dir = DEFAULT_CONFIG["output_dir"]
    
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

# ==========================================
# Core Visualization Class
# ==========================================

class AdvancedVisualizer:
    """Advanced visualization capabilities for cognitive simulations"""
    
    def __init__(self, log_directory: str = "simulation_logs", config: Optional[Dict[str, Any]] = None):
        """Initialize the advanced visualization system.
        
        Args:
            log_directory: Directory containing simulation logs
            config: Configuration dictionary
        """
        self.log_directory = log_directory
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
        
        # Configure matplotlib style
        if HAS_MATPLOTLIB:
            configure_matplotlib_style(self.config["style"])
        
        # Create output directory
        self.output_dir = ensure_output_directory(self.config.get("output_dir"))
        
        # Initialize cache for loaded data
        self.data_cache = {}
    
    def load_simulation(self, simulation_id: Optional[str] = None) -> Dict[str, Any]:
        """Load data for a specific simulation with caching.
        
        Args:
            simulation_id: ID of the simulation to load (default: latest)
            
        Returns:
            Dictionary containing simulation data
        """
        if simulation_id is None:
            simulation_id = get_latest_simulation_id(self.log_directory)
            if simulation_id is None:
                logger.error("No simulation logs found")
                return {}
        
        # Check cache first
        if simulation_id in self.data_cache:
            return self.data_cache[simulation_id]
        
        # Load data and update cache
        data = load_simulation_data(simulation_id, self.log_directory)
        if data:
            self.data_cache[simulation_id] = data
        
        return data
    
    def load_multiple_simulations(self, simulation_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Load data for multiple simulations.
        
        Args:
            simulation_ids: List of simulation IDs to load
            
        Returns:
            Dictionary mapping simulation IDs to simulation data
        """
        results = {}
        for sim_id in simulation_ids:
            data = self.load_simulation(sim_id)
            if data:
                results[sim_id] = data
        
        return results
    
    def plot_energy_trajectory(self, simulation_id: Optional[str] = None, 
                               show: bool = True, save: bool = False) -> Optional[Union[plt.Figure, go.Figure]]:
        """Plot the energy trajectory with advanced visualizations.
        
        Args:
            simulation_id: ID of the simulation to visualize (default: latest)
            show: Whether to display the plot
            save: Whether to save the plot to a file
            
        Returns:
            Figure object if available
        """
        data = self.load_simulation(simulation_id)
        if not data:
            return None
        
        sim_id = data.get("simulation_id", simulation_id)
        
        # Choose visualization library based on config and availability
        if self.config["interactive"] and HAS_PLOTLY:
            return self._plot_energy_trajectory_plotly(data, sim_id, show, save)
        elif HAS_MATPLOTLIB:
            return self._plot_energy_trajectory_mpl(data, sim_id, show, save)
        else:
            logger.error("No visualization libraries available")
            return None
    
    def _plot_energy_trajectory_mpl(self, data: Dict[str, Any], sim_id: str,
                                    show: bool, save: bool) -> Optional[plt.Figure]:
        """Plot energy trajectory using matplotlib."""
        if "data" not in data or "iterations" not in data["data"] or "energy_levels" not in data["data"]:
            logger.error("Energy data not available")
            return None
        
        iterations = data["data"]["iterations"]
        energy_levels = data["data"]["energy_levels"]
        
        fig, ax = plt.subplots(figsize=self.config["default_figsize"])
        
        # Plot energy levels
        line, = ax.plot(iterations, energy_levels, label="Energy Level", 
                       linewidth=self.config["line_width"])
        
        # Add a threshold line for critical energy
        ax.axhline(y=0.2, color='red', linestyle='--', alpha=0.5, label="Critical Energy")
        
        # Highlight regions where energy is below critical threshold
        if iterations and energy_levels:
            critical_mask = np.array(energy_levels) < 0.2
            critical_regions = []
            start_idx = None
            
            for i, is_critical in enumerate(critical_mask):
                if is_critical and start_idx is None:
                    start_idx = i
                elif not is_critical and start_idx is not None:
                    critical_regions.append((start_idx, i))
                    start_idx = None
            
            if start_idx is not None:
                critical_regions.append((start_idx, len(iterations)-1))
            
            for start, end in critical_regions:
                ax.axvspan(iterations[start], iterations[end], color='red', alpha=0.2)
        
        # Add markers for specific events if available
        if "state_history" in data:
            consume_actions = [(state["age"], state["energy"]) 
                              for state in data["state_history"] 
                              if state["action"]["type"] == "consume" and state["action"]["success"]]
            
            if consume_actions:
                ages, energies = zip(*consume_actions)
                ax.scatter(ages, energies, color='green', s=self.config["marker_size"]*2, 
                          marker='^', label="Consume Energy", zorder=10)
        
        # Customize appearance
        ax.set_title(f"Energy Trajectory - Simulation {sim_id}")
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Energy Level")
        ax.grid(self.config["show_grid"], alpha=0.3)
        ax.legend(loc='best')
        
        # Add annotations for significant events
        if iterations and energy_levels:
            min_idx = np.argmin(energy_levels)
            max_idx = np.argmax(energy_levels)
            
            ax.annotate(f"Min: {energy_levels[min_idx]:.2f}", 
                       xy=(iterations[min_idx], energy_levels[min_idx]),
                       xytext=(10, -20), textcoords="offset points",
                       arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
            
            ax.annotate(f"Max: {energy_levels[max_idx]:.2f}", 
                       xy=(iterations[max_idx], energy_levels[max_idx]),
                       xytext=(10, 20), textcoords="offset points",
                       arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
        
        plt.tight_layout()
        
        if save:
            output_path = os.path.join(self.output_dir, f"{sim_id}_energy_trajectory.{self.config['export_format']}")
            plt.savefig(output_path, dpi=self.config["export_dpi"], bbox_inches="tight")
            logger.info(f"Saved energy trajectory plot to {output_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def _plot_energy_trajectory_plotly(self, data: Dict[str, Any], sim_id: str,
                                      show: bool, save: bool) -> Optional[go.Figure]:
        """Plot energy trajectory using plotly."""
        if "data" not in data or "iterations" not in data["data"] or "energy_levels" not in data["data"]:
            logger.error("Energy data not available")
            return None
        
        iterations = data["data"]["iterations"]
        energy_levels = data["data"]["energy_levels"]
        
        fig = go.Figure()
        
        # Add energy level line
        fig.add_trace(go.Scatter(
            x=iterations,
            y=energy_levels,
            mode='lines',
            name='Energy Level',
            line=dict(width=3, color='blue')
        ))
        
        # Add critical threshold line
        fig.add_trace(go.Scatter(
            x=[min(iterations), max(iterations)],
            y=[0.2, 0.2],
            mode='lines',
            name='Critical Energy',
            line=dict(width=2, color='red', dash='dash')
        ))
        
        # Add consume actions if available
        if "state_history" in data:
            consume_actions = [(state["age"], state["energy"]) 
                              for state in data["state_history"] 
                              if state["action"]["type"] == "consume" and state["action"]["success"]]
            
            if consume_actions:
                ages, energies = zip(*consume_actions)
                fig.add_trace(go.Scatter(
                    x=ages,
                    y=energies,
                    mode='markers',
                    name='Consume Energy',
                    marker=dict(size=10, color='green', symbol='triangle-up')
                ))
        
        # Customize layout
        fig.update_layout(
            title=f"Energy Trajectory - Simulation {sim_id}",
            xaxis_title="Iteration",
            yaxis_title="Energy Level",
            legend=dict(x=0.01, y=0.99),
            hovermode="closest",
            template="plotly_white"
        )
        
        # Add shapes for critical regions
        if iterations and energy_levels:
            critical_mask = np.array(energy_levels) < 0.2
            critical_regions = []
            start_idx = None
            
            for i, is_critical in enumerate(critical_mask):
                if is_critical and start_idx is None:
                    start_idx = i
                elif not is_critical and start_idx is not None:
                    critical_regions.append((start_idx, i))
                    start_idx = None
            
            if start_idx is not None:
                critical_regions.append((start_idx, len(iterations)-1))
            
            shapes = []
            for start, end in critical_regions:
                shapes.append(dict(
                    type="rect",
                    x0=iterations[start],
                    x1=iterations[end],
                    y0=0,
                    y1=1,
                    xref="x",
                    yref="paper",
                    fillcolor="red",
                    opacity=0.2,
                    layer="below",
                    line_width=0
                ))
            
            fig.update_layout(shapes=shapes)
        
        if save:
            output_path = os.path.join(self.output_dir, f"{sim_id}_energy_trajectory.html")
            fig.write_html(output_path)
            logger.info(f"Saved interactive energy trajectory plot to {output_path}")
        
        if show:
            fig.show()
        
        return fig
    
    def plot_performance_metrics(self, simulation_id: Optional[str] = None,
                                show: bool = True, save: bool = False) -> Optional[Union[plt.Figure, go.Figure]]:
        """Plot performance metrics with advanced visualizations.
        
        Args:
            simulation_id: ID of the simulation to visualize (default: latest)
            show: Whether to display the plot
            save: Whether to save the plot to a file
            
        Returns:
            Figure object if available
        """
        data = self.load_simulation(simulation_id)
        if not data:
            return None
        
        sim_id = data.get("simulation_id", simulation_id)
        
        # Choose visualization library based on config and availability
        if self.config["interactive"] and HAS_PLOTLY:
            return self._plot_performance_metrics_plotly(data, sim_id, show, save)
        elif HAS_MATPLOTLIB:
            return self._plot_performance_metrics_mpl(data, sim_id, show, save)
        else:
            logger.error("No visualization libraries available")
            return None
    
    def _plot_performance_metrics_mpl(self, data: Dict[str, Any], sim_id: str,
                                     show: bool, save: bool) -> Optional[plt.Figure]:
        """Plot performance metrics using matplotlib."""
        if "data" not in data or "iterations" not in data["data"] or "performance_metrics" not in data["data"]:
            logger.error("Performance metrics data not available")
            return None
        
        iterations = data["data"]["iterations"]
        metrics = data["data"]["performance_metrics"]
        
        if not metrics:
            logger.error("No performance metrics available")
            return None
        
        # Create a 2x2 grid for the metrics
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()
        
        colors = {
            "survival": "red",
            "efficiency": "blue",
            "learning": "green",
            "adaptation": "purple"
        }
        
        for i, (metric, values) in enumerate(metrics.items()):
            if i >= len(axes):
                logger.warning(f"Too many metrics to display, skipping {metric}")
                continue
                
            ax = axes[i]
            
            # Plot the metric
            ax.plot(iterations, values, label=metric.capitalize(), 
                   color=colors.get(metric, "black"), linewidth=self.config["line_width"])
            
            # Add trend line using polynomial fit
            if len(iterations) > 5:
                z = np.polyfit(iterations, values, 3)
                p = np.poly1d(z)
                ax.plot(iterations, p(iterations), "--", color="gray", alpha=0.7, 
                       label=f"{metric.capitalize()} Trend")
            
            # Customize appearance
            ax.set_title(f"{metric.capitalize()}")
            ax.set_xlabel("Iteration")
            ax.set_ylabel("Score")
            ax.set_ylim(0, 1.05)
            ax.grid(self.config["show_grid"], alpha=0.3)
            ax.legend(loc='best')
        
        # Overall title
        plt.suptitle(f"Performance Metrics - Simulation {sim_id}", 
                    fontsize=self.config["font_size"] + 4, y=1.02)
        
        plt.tight_layout()
        
        if save:
            output_path = os.path.join(self.output_dir, f"{sim_id}_performance_metrics.{self.config['export_format']}")
            plt.savefig(output_path, dpi=self.config["export_dpi"], bbox_inches="tight")
            logger.info(f"Saved performance metrics plot to {output_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def _plot_performance_metrics_plotly(self, data: Dict[str, Any], sim_id: str,
                                        show: bool, save: bool) -> Optional[go.Figure]:
        """Plot performance metrics using plotly."""
        if "data" not in data or "iterations" not in data["data"] or "performance_metrics" not in data["data"]:
            logger.error("Performance metrics data not available")
            return None
        
        iterations = data["data"]["iterations"]
        metrics = data["data"]["performance_metrics"]
        
        if not metrics:
            logger.error("No performance metrics available")
            return None
        
        # Create a 2x2 grid for the metrics
        fig = make_subplots(rows=2, cols=2, 
                           subplot_titles=[metric.capitalize() for metric in metrics.keys()],
                           shared_xaxes=True)
        
        colors = {
            "survival": "red",
            "efficiency": "blue",
            "learning": "green",
            "adaptation": "purple"
        }
        
        for i, (metric, values) in enumerate(metrics.items()):
            row = i // 2 + 1
            col = i % 2 + 1
            
            # Plot the metric
            fig.add_trace(
                go.Scatter(
                    x=iterations,
                    y=values,
                    mode='lines',
                    name=metric.capitalize(),
                    line=dict(color=colors.get(metric, "black"), width=3)
                ),
                row=row, col=col
            )
            
            # Add trend line using polynomial fit
            if len(iterations) > 5:
                z = np.polyfit(iterations, values, 3)
                p = np.poly1d(z)
                trend_values = p(iterations)
                
                fig.add_trace(
                    go.Scatter(
                        x=iterations,
                        y=trend_values,
                        mode='lines',
                        name=f"{metric.capitalize()} Trend",
                        line=dict(color="gray", width=2, dash='dash'),
                        showlegend=False
                    ),
                    row=row, col=col
                )
        
        # Update layout
        fig.update_layout(
            title=f"Performance Metrics - Simulation {sim_id}",
            height=700,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            template="plotly_white"
        )
        
        # Update all y-axes to have the same range
        for i in range(1, 5):
            fig.update_yaxes(range=[0, 1.05], row=(i+1)//2, col=(i+1)%2)
        
        if save:
            output_path = os.path.join(self.output_dir, f"{sim_id}_performance_metrics.html")
            fig.write_html(output_path)
            logger.info(f"Saved interactive performance metrics plot to {output_path}")
        
        if show:
            fig.show()
        
        return fig
    
    def plot_behavior_weights(self, simulation_id: Optional[str] = None,
                             show: bool = True, save: bool = False) -> Optional[Union[plt.Figure, go.Figure]]:
        """Plot behavior weights evolution with advanced visualizations.
        
        Args:
            simulation_id: ID of the simulation to visualize (default: latest)
            show: Whether to display the plot
            save: Whether to save the plot to a file
            
        Returns:
            Figure object if available
        """
        data = self.load_simulation(simulation_id)
        if not data:
            return None
        
        sim_id = data.get("simulation_id", simulation_id)
        
        # Choose visualization library based on config and availability
        if self.config["interactive"] and HAS_PLOTLY:
            return self._plot_behavior_weights_plotly(data, sim_id, show, save)
        elif HAS_MATPLOTLIB:
            return self._plot_behavior_weights_mpl(data, sim_id, show, save)
        else:
            logger.error("No visualization libraries available")
            return None
    
    def _plot_behavior_weights_mpl(self, data: Dict[str, Any], sim_id: str,
                                  show: bool, save: bool) -> Optional[plt.Figure]:
        """Plot behavior weights using matplotlib."""
        if "data" not in data or "iterations" not in data["data"] or "behavior_weights" not in data["data"]:
            logger.error("Behavior weights data not available")
            return None
        
        iterations = data["data"]["iterations"]
        behavior_weights = data["data"]["behavior_weights"]
        
        if not behavior_weights:
            logger.error("No behavior weights available")
            return None
        
        # Create the plot
        fig, ax = plt.subplots(figsize=self.config["default_figsize"])
        
        # Define colors for behaviors
        colors = {
            "move": "blue",
            "observe": "green",
            "consume": "red",
            "rest": "purple",
            "explore": "orange",
            "communicate": "brown"
        }
        
        # Plot each behavior weight
        for behavior, weights in behavior_weights.items():
            ax.plot(iterations, weights, label=behavior.capitalize(), 
                   color=colors.get(behavior, "black"), linewidth=self.config["line_width"])
        
        # Find the behavior with the highest final weight
        final_weights = {b: w[-1] for b, w in behavior_weights.items()}
        dominant_behavior = max(final_weights, key=final_weights.get)
        
        # Annotate the dominant behavior
        ax.annotate(f"Dominant: {dominant_behavior.capitalize()}", 
                   xy=(iterations[-1], final_weights[dominant_behavior]),
                   xytext=(10, 0), textcoords="offset points",
                   arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
        
        # Customize appearance
        ax.set_title(f"Behavior Weight Evolution - Simulation {sim_id}")
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Weight")
        ax.grid(self.config["show_grid"], alpha=0.3)
        ax.legend(loc='best')
        
        plt.tight_layout()
        
        if save:
            output_path = os.path.join(self.output_dir, f"{sim_id}_behavior_weights.{self.config['export_format']}")
            plt.savefig(output_path, dpi=self.config["export_dpi"], bbox_inches="tight")
            logger.info(f"Saved behavior weights plot to {output_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def _plot_behavior_weights_plotly(self, data: Dict[str, Any], sim_id: str,
                                     show: bool, save: bool) -> Optional[go.Figure]:
        """Plot behavior weights using plotly."""
        if "data" not in data or "iterations" not in data["data"] or "behavior_weights" not in data["data"]:
            logger.error("Behavior weights data not available")
            return None
        
        iterations = data["data"]["iterations"]
        behavior_weights = data["data"]["behavior_weights"]
        
        if not behavior_weights:
            logger.error("No behavior weights available")
            return None
        
        # Create figure
        fig = go.Figure()
        
        # Define colors for behaviors
        colors = {
            "move": "blue",
            "observe": "green",
            "consume": "red",
            "rest": "purple",
            "explore": "orange",
            "communicate": "brown"
        }
        
        # Add each behavior as a trace
        for behavior, weights in behavior_weights.items():
            fig.add_trace(go.Scatter(
                x=iterations,
                y=weights,
                mode='lines',
                name=behavior.capitalize(),
                line=dict(width=3, color=colors.get(behavior, "black"))
            ))
        
        # Add annotations for key points
        for behavior, weights in behavior_weights.items():
            # Find largest increase
            if len(weights) > 10:
                changes = [weights[i+10] - weights[i] for i in range(len(weights)-10)]
                max_change_idx = np.argmax(changes)
                if changes[max_change_idx] > 0.1:  # Only annotate significant changes
                    fig.add_annotation(
                        x=iterations[max_change_idx+5],
                        y=weights[max_change_idx+5],
                        text=f"{behavior.capitalize()} increasing",
                        showarrow=True,
                        arrowhead=2,
                        arrowcolor=colors.get(behavior, "black"),
                        arrowwidth=1,
                        arrowsize=1
                    )
        
        # Customize layout
        fig.update_layout(
            title=f"Behavior Weight Evolution - Simulation {sim_id}",
            xaxis_title="Iteration",
            yaxis_title="Weight",
            legend=dict(x=0.01, y=0.99),
            hovermode="closest",
            template="plotly_white"
        )
        
        if save:
            output_path = os.path.join(self.output_dir, f"{sim_id}_behavior_weights.html")
            fig.write_html(output_path)
            logger.info(f"Saved interactive behavior weights plot to {output_path}")
        
        if show:
            fig.show()
        
        return fig
