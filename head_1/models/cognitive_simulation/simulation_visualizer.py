import os
import json
import glob
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional
from matplotlib.figure import Figure
from datetime import datetime

class SimulationVisualizer:
    """Visualizes results from cognitive simulations"""
    
    def __init__(self, log_directory: str = "simulation_logs"):
        self.log_directory = log_directory
        
    def find_simulation_logs(self, simulation_id: Optional[str] = None) -> List[str]:
        """Find all simulation logs or logs for a specific simulation ID"""
        pattern = f"{simulation_id}_*.json" if simulation_id else "*.json"
        return glob.glob(os.path.join(self.log_directory, pattern))
    
    def get_latest_simulation_id(self) -> Optional[str]:
        """Get the ID of the most recent simulation"""
        log_files = glob.glob(os.path.join(self.log_directory, "sim_*_final.json"))
        if not log_files:
            return None
            
        # Sort by modification time (newest first)
        log_files.sort(key=os.path.getmtime, reverse=True)
        # Extract simulation ID from filename (sim_1234567890_final.json -> sim_1234567890)
        latest_file = os.path.basename(log_files[0])
        return latest_file.split('_final.json')[0]
        
    def load_simulation_data(self, simulation_id: str) -> Dict[str, Any]:
        """Load data for a specific simulation"""
        data = {
            "iterations": [],
            "energy_levels": [],
            "obstacles": [],
            "rewards": [],
            "environment_conditions": [],
            "performance_metrics": {},
            "behavior_weights": {},
            "final_state": None
        }
        
        # Load all log files for this simulation
        log_files = self.find_simulation_logs(simulation_id)
        log_files.sort(key=lambda x: int(os.path.basename(x).split('_')[-1].split('.')[0]) 
                      if not os.path.basename(x).endswith('final.json') else float('inf'))
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
                
                # Store iteration data
                if "iteration" in log_data:
                    data["iterations"].append(log_data["iteration"])
                    
                    # Energy levels
                    if "lifeform" in log_data and "energy_percentage" in log_data["lifeform"]:
                        data["energy_levels"].append(log_data["lifeform"]["energy_percentage"])
                    
                    # Environment state
                    if "environment" in log_data:
                        env = log_data["environment"]
                        data["obstacles"].append(env.get("obstacles", 0))
                        data["rewards"].append(env.get("rewards", 0))
                        data["environment_conditions"].append(env.get("environmental_condition", 0))
                    
                    # Performance metrics
                    if "lifeform" in log_data and "performance_metrics" in log_data["lifeform"]:
                        metrics = log_data["lifeform"]["performance_metrics"]
                        for key, value in metrics.items():
                            if key not in data["performance_metrics"]:
                                data["performance_metrics"][key] = []
                            data["performance_metrics"][key].append(value)
                    
                    # Behavior weights
                    if "lifeform" in log_data and "behavior_weights" in log_data["lifeform"]:
                        weights = log_data["lifeform"]["behavior_weights"]
                        for key, value in weights.items():
                            if key not in data["behavior_weights"]:
                                data["behavior_weights"][key] = []
                            data["behavior_weights"][key].append(value)
                
                # Store final state data
                if os.path.basename(log_file).endswith('final.json'):
                    data["final_state"] = log_data
            
            except Exception as e:
                print(f"Error loading log file {log_file}: {str(e)}")
        
        return data
    
    def plot_energy_levels(self, data: Dict[str, Any], show: bool = True) -> Figure:
        """Plot energy levels over time"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if data["iterations"] and data["energy_levels"]:
            ax.plot(data["iterations"], data["energy_levels"], 'b-', label='Energy Level')
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Energy Level (%)')
            ax.set_title('Lifeform Energy Levels Over Time')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 1.05)
            
            # Add a horizontal line at 20% energy as a "danger zone"
            ax.axhline(y=0.2, color='r', linestyle='--', alpha=0.5, label='Low Energy Warning')
            
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'No energy data available', ha='center', va='center')
        
        if show:
            plt.tight_layout()
            plt.show()
            
        return fig
    
    def plot_environment_conditions(self, data: Dict[str, Any], show: bool = True) -> Figure:
        """Plot environmental conditions over time"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if data["iterations"]:
            if data["obstacles"]:
                ax.plot(data["iterations"], data["obstacles"], 'r-', label='Obstacles')
            if data["rewards"]:
                ax.plot(data["iterations"], data["rewards"], 'g-', label='Rewards')
            if data["environment_conditions"]:
                ax.plot(data["iterations"], data["environment_conditions"], 'b-', label='Environmental Conditions')
                
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Intensity')
            ax.set_title('Environmental Conditions Over Time')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 1.05)
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'No environment data available', ha='center', va='center')
        
        if show:
            plt.tight_layout()
            plt.show()
            
        return fig
    
    def plot_performance_metrics(self, data: Dict[str, Any], show: bool = True) -> Figure:
        """Plot performance metrics over time"""
        metrics = data["performance_metrics"]
        if not metrics or not data["iterations"]:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No performance metrics available', ha='center', va='center')
            return fig
            
        # Create a multi-line chart for all metrics
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        color_idx = 0
        
        for key, values in metrics.items():
            if len(values) == len(data["iterations"]):
                ax.plot(data["iterations"], values, f'{colors[color_idx]}-', label=key.capitalize())
                color_idx = (color_idx + 1) % len(colors)
        
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Score')
        ax.set_title('Performance Metrics Over Time')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.05)
        ax.legend()
        
        if show:
            plt.tight_layout()
            plt.show()
            
        return fig
    
    def plot_behavior_weights(self, data: Dict[str, Any], show: bool = True) -> Figure:
        """Plot behavior weights over time to show adaptation"""
        weights = data["behavior_weights"]
        if not weights or not data["iterations"]:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No behavior weight data available', ha='center', va='center')
            return fig
            
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        color_idx = 0
        
        # Sample the iterations to reduce visual clutter if there are many
        if len(data["iterations"]) > 50:
            sample_rate = len(data["iterations"]) // 50
            sample_indices = range(0, len(data["iterations"]), sample_rate)
            sampled_iterations = [data["iterations"][i] for i in sample_indices]
        else:
            sample_indices = range(len(data["iterations"]))
            sampled_iterations = data["iterations"]
        
        for key, values in weights.items():
            if len(values) == len(data["iterations"]):
                sampled_values = [values[i] for i in sample_indices]
                ax.plot(sampled_iterations, sampled_values, f'{colors[color_idx]}-', label=key)
                color_idx = (color_idx + 1) % len(colors)
        
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Weight')
        ax.set_title('Behavior Weights Over Time (Adaptation)')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        if show:
            plt.tight_layout()
            plt.show()
            
        return fig
    
    def generate_summary_report(self, simulation_id: Optional[str] = None, show_plots: bool = True) -> None:
        """Generate a comprehensive summary report of a simulation"""
        if simulation_id is None:
            simulation_id = self.get_latest_simulation_id()
            if simulation_id is None:
                print("No simulation logs found.")
                return
        
        print(f"\n{'='*60}")
        print(f"SIMULATION SUMMARY REPORT - {simulation_id}")
        print(f"{'='*60}")
        
        data = self.load_simulation_data(simulation_id)
        
        if not data["iterations"]:
            print("No data available for this simulation.")
            return
        
        # Print basic information
        final_state = data["final_state"]
        if final_state:
            print(f"\n--- Simulation Overview ---")
            
            sim_time = datetime.fromtimestamp(final_state.get("timestamp", 0))
            print(f"Date: {sim_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if "lifeform" in final_state:
                lifeform = final_state["lifeform"]
                print(f"Lifeform: {lifeform.get('name', 'Unknown')}")
                print(f"Total Iterations: {final_state.get('iteration', 0)}")
                print(f"Actions Taken: {lifeform.get('actions_taken', 0)}")
                print(f"Energy Consumed: {lifeform.get('lifetime_energy_consumed', 0):.2f}")
                
                # Calculate survival ratio
                energy_percent = lifeform.get('energy_percentage', 0) * 100
                print(f"Final Energy: {energy_percent:.1f}%")
            
            if "final_statistics" in final_state:
                stats = final_state["final_statistics"]
                print(f"\n--- Final Statistics ---")
                print(f"Survival Time: {stats.get('survival_time', 0)} iterations")
                
                # Calculate average energy
                if "avg_energy" in stats:
                    print(f"Average Energy Level: {stats.get('avg_energy', 0) * 100:.1f}%")
            
            if "lifeform" in final_state and "performance_metrics" in final_state["lifeform"]:
                print(f"\n--- Performance Metrics ---")
                for key, value in final_state["lifeform"]["performance_metrics"].items():
                    print(f"{key.capitalize()}: {value:.2f}")
        
        # Generate plots
        if show_plots:
            self.plot_energy_levels(data)
            self.plot_environment_conditions(data)
            self.plot_performance_metrics(data)
            self.plot_behavior_weights(data)
        
        print(f"\n{'='*60}")
        print(f"END OF REPORT - {simulation_id}")
        print(f"{'='*60}\n")
        
    def save_report_plots(self, simulation_id: Optional[str] = None, 
                          output_dir: Optional[str] = None) -> None:
        """Save all plots for a simulation to files"""
        if simulation_id is None:
            simulation_id = self.get_latest_simulation_id()
            if simulation_id is None:
                print("No simulation logs found.")
                return
        
        if output_dir is None:
            output_dir = os.path.join(self.log_directory, f"{simulation_id}_plots")
        
        os.makedirs(output_dir, exist_ok=True)
        
        data = self.load_simulation_data(simulation_id)
        
        if not data["iterations"]:
            print("No data available for this simulation.")
            return
        
        # Generate and save plots
        plots = [
            ("energy", self.plot_energy_levels(data, show=False)),
            ("environment", self.plot_environment_conditions(data, show=False)),
            ("performance", self.plot_performance_metrics(data, show=False)),
            ("behavior", self.plot_behavior_weights(data, show=False))
        ]
        
        for name, fig in plots:
            filename = os.path.join(output_dir, f"{simulation_id}_{name}.png")
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Saved plot to {filename}")


def main():
    """Run the visualization tool on the latest simulation"""
    visualizer = SimulationVisualizer()
    latest_sim_id = visualizer.get_latest_simulation_id()
    
    if latest_sim_id:
        print(f"Analyzing latest simulation: {latest_sim_id}")
        visualizer.generate_summary_report(latest_sim_id)
    else:
        print("No simulation logs found.")

if __name__ == "__main__":
    main()