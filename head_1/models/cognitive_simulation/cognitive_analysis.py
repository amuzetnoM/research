import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from datetime import datetime
from simulation_visualizer import SimulationVisualizer

class CognitiveAnalysis:
    """Advanced analysis of cognitive simulation data"""
    
    def __init__(self, log_directory: str = "simulation_logs"):
        self.log_directory = log_directory
        self.visualizer = SimulationVisualizer(log_directory)
        
    def load_simulation_data_as_df(self, simulation_id: Optional[str] = None) -> pd.DataFrame:
        """Load simulation data and convert to pandas DataFrame for analysis"""
        if simulation_id is None:
            simulation_id = self.visualizer.get_latest_simulation_id()
        
        if simulation_id is None:
            raise ValueError("No simulation logs found")
        
        # Load raw data
        data = self.visualizer.load_simulation_data(simulation_id)
        
        if not data["iterations"]:
            raise ValueError(f"No data available for simulation {simulation_id}")
        
        # Create a basic DataFrame with iterations
        df = pd.DataFrame({"iteration": data["iterations"]})
        
        # Add energy levels
        if data["energy_levels"]:
            df["energy_level"] = data["energy_levels"]
        
        # Add environment data
        if data["obstacles"]:
            df["obstacles"] = data["obstacles"]
        if data["rewards"]:
            df["rewards"] = data["rewards"]
        if data["environment_conditions"]:
            df["environment_condition"] = data["environment_conditions"]
        
        # Add performance metrics
        for metric, values in data["performance_metrics"].items():
            if len(values) == len(data["iterations"]):
                df[f"metric_{metric}"] = values
        
        # Add behavior weights
        for behavior, values in data["behavior_weights"].items():
            if len(values) == len(data["iterations"]):
                df[f"weight_{behavior}"] = values
        
        return df
    
    def _compute_correlations(self, df: pd.DataFrame, correlation_cols: List[str]) -> Dict[str, float]:
        """Helper method to compute correlations between energy level and other factors"""
        correlations = {}
        for col in correlation_cols:
            if df[col].dtype in [np.float64, np.int64]:
                corr = df["energy_level"].corr(df[col])
                correlations[col] = corr
        return correlations
    
    def analyze_survival_factors(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze factors that contribute to survival"""
        if "energy_level" not in df.columns:
            return {"error": "Energy level data not available"}

        results = {}

        # Check which factors correlate with energy level
        correlation_cols = [col for col in df.columns if col not in ("energy_level", "iteration")]
        if correlation_cols:
            self._extracted_from_analyze_survival_factors_11(df, correlation_cols, results)
        # Analyze energy trends
        results["energy_trends"] = {
            "initial": df["energy_level"].iloc[0],
            "final": df["energy_level"].iloc[-1],
            "min": df["energy_level"].min(),
            "max": df["energy_level"].max(),
            "mean": df["energy_level"].mean(),
            "median": df["energy_level"].median(),
            "std": df["energy_level"].std()
        }

        # Linear regression for energy trend over time
        x = df["iteration"].values.reshape(-1, 1)
        y = df["energy_level"].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x.flatten(), y)

        results["energy_regression"] = {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value**2,
            "p_value": p_value,
            "std_err": std_err,
            "trend": "increasing" if slope > 0 else "decreasing",
            "significance": "significant" if p_value < 0.05 else "not significant"
        }

        return results

    # TODO Rename this here and in `analyze_survival_factors`
    def _extracted_from_analyze_survival_factors_11(self, df, correlation_cols, results):
        correlations = self._compute_correlations(df, correlation_cols)

        # Sort by absolute correlation
        sorted_correlations = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        results["correlations"] = sorted_correlations

        # Top positive and negative factors
        pos_factors = [(k, v) for k, v in sorted_correlations if v > 0][:3]
        neg_factors = [(k, v) for k, v in sorted_correlations if v < 0][:3]

        results["top_positive_factors"] = pos_factors
        results["top_negative_factors"] = neg_factors
    
    def analyze_behavior_adaptation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze how behaviors adapt over time"""
        # Get behavior weight columns
        weight_cols = [col for col in df.columns if col.startswith("weight_")]
        if not weight_cols:
            return {"error": "Behavior weight data not available"}
        
        # Analysis of weight changes
        weight_changes = {}
        for col in weight_cols:
            behavior = col.replace("weight_", "")
            initial = df[col].iloc[0]
            final = df[col].iloc[-1]
            change = final - initial
            percent_change = (change / initial) * 100 if initial != 0 else float('inf')
            
            weight_changes[behavior] = {
                "initial": initial,
                "final": final,
                "change": change,
                "percent_change": percent_change
            }
        
        # Sort behaviors by amount of adaptation
        sorted_adaptation = sorted(
            [(k, abs(v["percent_change"])) for k, v in weight_changes.items()], 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Analyze if behaviors converge or diverge
        initial_variance = np.var([w["initial"] for w in weight_changes.values()])
        final_variance = np.var([w["final"] for w in weight_changes.values()])
        
        results = {
            "weight_changes": weight_changes,
            "most_adapted_behaviors": sorted_adaptation,
            "behavior_specialization": {
                "initial_variance": initial_variance,
                "final_variance": final_variance,
                "variance_change": final_variance - initial_variance,
                "pattern": "specializing" if final_variance > initial_variance else "generalizing"
            }
        }
        
        # Check if adaptation is still occurring at the end
        if len(df) > 10:
            recent_df = df.iloc[-10:]
            is_still_adapting = any(abs(recent_df[col].iloc[-1] - recent_df[col].iloc[0]) > 0.01 for col in weight_cols)
            results["adaptation_status"] = "still_adapting" if is_still_adapting else "stabilized"
        
        return results
    
    def analyze_environmental_impact(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze how the environment affects lifeform behavior and performance"""
        env_cols = ["environment_condition", "obstacles", "rewards"]

        if any(col not in df.columns for col in env_cols):
            return {"error": "Environment data not available"}

        # Correlations between environment and behaviors
        weight_cols = [col for col in df.columns if col.startswith("weight_")]

        env_behavior_corr = {}
        for env_col in env_cols:
            env_behavior_corr[env_col] = {}
            for weight_col in weight_cols:
                behavior = weight_col.replace("weight_", "")
                corr = df[env_col].corr(df[weight_col])
                env_behavior_corr[env_col][behavior] = corr

        results = {"environment_behavior_correlations": env_behavior_corr}
        # Check how environment affects energy levels
        if "energy_level" in df.columns:
            env_energy_corr = {}
            for env_col in env_cols:
                corr = df[env_col].corr(df["energy_level"])
                env_energy_corr[env_col] = corr

            results["environment_energy_correlations"] = env_energy_corr

            # Identify most challenging environmental conditions
            low_energy_periods = df[df["energy_level"] < 0.3]
            if not low_energy_periods.empty:
                avg_env_conditions = {
                    "environment_condition": low_energy_periods["environment_condition"].mean(),
                    "obstacles": low_energy_periods["obstacles"].mean(),
                    "rewards": low_energy_periods["rewards"].mean()
                }
                results["challenging_environments"] = avg_env_conditions

        # Environment stability analysis
        results["environment_stability"] = {
            "environment_condition_variance": df["environment_condition"].var(),
            "obstacles_variance": df["obstacles"].var(),
            "rewards_variance": df["rewards"].var()
        }

        return results
    
    def _prepare_cluster_data(self, df: pd.DataFrame, n_clusters: int = 3):
        """Prepare data for clustering analysis"""
        # Select numerical columns for clustering
        num_cols = [col for col in df.columns if df[col].dtype in [np.float64, np.int64] and col != "iteration"]
        if len(num_cols) < 3:
            return None, None, None, None
        
        # Prepare data for clustering
        X = df[num_cols].values
        
        # Normalize data
        X_norm = (X - X.mean(axis=0)) / X.std(axis=0)
        
        # Perform PCA to reduce dimensionality
        pca = PCA(n_components=min(3, len(num_cols)))
        X_pca = pca.fit_transform(X_norm)
        
        # Perform KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_pca)
        
        return num_cols, X_norm, pca, X_pca, kmeans, clusters
    
    def _create_operational_mode(self, i: int, cluster_stats: Dict[str, Any], num_cols: List[str]) -> Dict[str, Any]:
        """Create an operational mode description for a cluster"""
        mode = {"cluster": i, "size_percentage": cluster_stats["percentage"]}
        
        # Check energy level
        if "energy_level_mean" in cluster_stats:
            energy_level = cluster_stats["energy_level_mean"]
            if energy_level > 0.7:
                mode["energy_status"] = "high"
            elif energy_level < 0.3:
                mode["energy_status"] = "critical"
            else:
                mode["energy_status"] = "moderate"
        
        # Check environment
        if "obstacles_mean" in cluster_stats and "rewards_mean" in cluster_stats:
            obstacles = cluster_stats["obstacles_mean"]
            rewards = cluster_stats["rewards_mean"]
            
            if obstacles > 0.6:
                mode["environment_type"] = "hostile"
            elif rewards > 0.5:
                mode["environment_type"] = "abundant"
            elif obstacles < 0.2 and rewards < 0.2:
                mode["environment_type"] = "barren"
            else:
                mode["environment_type"] = "balanced"
        
        # Check behavioral emphasis
        max_weight = -float('inf')
        dominant_behavior = None
        
        for col in [c for c in num_cols if c.startswith("weight_")]:
            behavior = col.replace("weight_", "")
            weight = cluster_stats[f"{col}_mean"]
            
            if weight > max_weight:
                max_weight = weight
                dominant_behavior = behavior
        
        if dominant_behavior:
            mode["dominant_behavior"] = dominant_behavior
        
        # Determine a descriptive name for this mode
        if all(key in mode for key in ["energy_status", "environment_type", "dominant_behavior"]):
            mode["name"] = f"{mode['energy_status']}_{mode['environment_type']}_{mode['dominant_behavior']}"
        else:
            mode["name"] = f"cluster_{i}"
        
        return mode
    
    def perform_cluster_analysis(self, df: pd.DataFrame, n_clusters: int = 3) -> Dict[str, Any]:
        """Perform cluster analysis to identify different operational modes"""
        result = self._prepare_cluster_data(df, n_clusters)
        if result is None:
            return {"error": "Not enough numerical data for clustering"}
        
        num_cols, X_norm, pca, X_pca, kmeans, clusters = result
        
        # Add cluster labels to DataFrame
        df_with_clusters = df.copy()
        df_with_clusters["cluster"] = clusters
        
        # Analyze clusters
        cluster_analysis = {}
        
        for i in range(n_clusters):
            cluster_df = df_with_clusters[df_with_clusters["cluster"] == i]
            
            # Calculate cluster statistics
            cluster_stats = {
                "size": len(cluster_df),
                "percentage": (len(cluster_df) / len(df)) * 100
            }
            
            # For each numerical column, calculate mean and std for this cluster
            for col in num_cols:
                cluster_stats[f"{col}_mean"] = cluster_df[col].mean()
                cluster_stats[f"{col}_std"] = cluster_df[col].std()
            
            cluster_analysis[f"cluster_{i}"] = cluster_stats
        
        # Determine operational modes based on clusters
        operational_modes = []
        for i in range(n_clusters):
            mode = self._create_operational_mode(i, cluster_analysis[f"cluster_{i}"], num_cols)
            operational_modes.append(mode)
        
        return {
            "pca_explained_variance": pca.explained_variance_ratio_.tolist(),
            "cluster_analysis": cluster_analysis,
            "operational_modes": operational_modes,
            "n_clusters": n_clusters
        }
    
    def _calculate_learning_segment_metrics(self, segment: pd.DataFrame, i: int) -> Dict[str, Any]:
        """Calculate learning metrics for a time segment"""
        # Average efficiency in this segment
        avg_efficiency = segment["metric_efficiency"].mean()
        
        # Calculate stability (lower variance = more stable)
        efficiency_stability = 1.0 - segment["metric_efficiency"].var()
        
        # Energy conservation
        if "energy_level" in segment.columns:
            energy_stability = 1.0 - segment["energy_level"].var()
            avg_energy = segment["energy_level"].mean()
        else:
            energy_stability = None
            avg_energy = None
        
        return {
            "segment": i,
            "start_iteration": segment["iteration"].iloc[0],
            "end_iteration": segment["iteration"].iloc[-1],
            "avg_efficiency": avg_efficiency,
            "efficiency_stability": efficiency_stability,
            "avg_energy": avg_energy,
            "energy_stability": energy_stability
        }
    
    def _calculate_learning_rate(self, learning_progression: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate learning rate from progression data"""
        first_segment = learning_progression[0]
        last_segment = learning_progression[-1]
        
        efficiency_improvement = last_segment["avg_efficiency"] - first_segment["avg_efficiency"]
        stability_improvement = last_segment["efficiency_stability"] - first_segment["efficiency_stability"]
        
        # Calculate learning rate as combination of efficiency and stability improvements
        learning_rate = (efficiency_improvement + stability_improvement) / 2
        
        # Classify learning progress
        if learning_rate > 0.2:
            learning_category = "exceptional"
        elif learning_rate > 0.1:
            learning_category = "good"
        elif learning_rate > 0:
            learning_category = "moderate"
        elif learning_rate > -0.1:
            learning_category = "stagnant"
        else:
            learning_category = "regressing"
        
        return {
            "learning_rate": learning_rate,
            "learning_category": learning_category
        }
    
    def analyze_learning_effectiveness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze how effectively the lifeform learns and adapts"""
        if "metric_efficiency" not in df.columns or len(df) < 10:
            return {"error": "Efficiency metric data not available or insufficient data points"}

        # Split data into time segments
        segment_size = max(10, len(df) // 5)  # At least 10 points per segment, or 5 segments total
        segments = []

        for i in range(0, len(df), segment_size):
            segment = df.iloc[i:min(i + segment_size, len(df))]
            if len(segment) >= 5:  # Only include reasonably sized segments
                segments.append(segment)

        # Calculate learning metrics across segments
        learning_progression = [
            self._calculate_learning_segment_metrics(segment, i) 
            for i, segment in enumerate(segments)
        ]

        results = {"learning_progression": learning_progression}

        # Calculate learning rate
        if len(learning_progression) >= 2:
            learning_rate_data = self._calculate_learning_rate(learning_progression)
            results.update(learning_rate_data)

        # Check for plateaus in learning
        if "metric_efficiency" in df.columns and len(df) > 20:
            self._extracted_from_analyze_learning_effectiveness_31(df, results)
        return results

    # TODO Rename this here and in `analyze_learning_effectiveness`
    def _extracted_from_analyze_learning_effectiveness_31(self, df, results):
        # Use rolling average to detect plateaus
        window_size = max(5, len(df) // 20)  # At least 5 points, or 5% of data
        rolling_efficiency = df["metric_efficiency"].rolling(window_size).mean()

        # Calculate derivatives to find flat regions (close to zero slope)
        derivatives = rolling_efficiency.diff().abs()
        plateaus = (derivatives < 0.01).astype(int)

        # Find contiguous plateau regions
        plateau_regions = []
        in_plateau = False
        plateau_start = 0

        for i in range(window_size, len(plateaus)):
            if plateaus.iloc[i] == 1 and not in_plateau:
                # Start of plateau
                in_plateau = True
                plateau_start = i
            elif (plateaus.iloc[i] == 0 or i == len(plateaus) - 1) and in_plateau:
                # End of plateau
                in_plateau = False
                plateau_length = i - plateau_start

                if plateau_length >= window_size:  # Only count significant plateaus
                    plateau_regions.append({
                        "start_iteration": df["iteration"].iloc[plateau_start],
                        "end_iteration": df["iteration"].iloc[i],
                        "length": plateau_length,
                        "efficiency_level": rolling_efficiency.iloc[plateau_start:i].mean()
                    })

        results["learning_plateaus"] = plateau_regions
        results["plateau_count"] = len(plateau_regions)
    
    def _load_and_analyze_data(self, simulation_id: str) -> Dict[str, Any]:
        """Load data and run all analyses for a simulation"""
        # Load data as DataFrame
        df = self.load_simulation_data_as_df(simulation_id)
        
        # Run analyses
        survival_analysis = self.analyze_survival_factors(df)
        behavior_analysis = self.analyze_behavior_adaptation(df)
        environment_analysis = self.analyze_environmental_impact(df)
        learning_analysis = self.analyze_learning_effectiveness(df)
        
        # Run cluster analysis with different numbers of clusters
        cluster_analysis_3 = self.perform_cluster_analysis(df, n_clusters=3)
        cluster_analysis_5 = self.perform_cluster_analysis(df, n_clusters=5)
        
        # Combine all analyses
        return {
            "df": df,
            "survival_analysis": survival_analysis,
            "behavior_analysis": behavior_analysis,
            "environment_analysis": environment_analysis,
            "learning_analysis": learning_analysis,
            "cluster_analysis_3": cluster_analysis_3,
            "cluster_analysis_5": cluster_analysis_5
        }
    
    def _evaluate_cognitive_capacity(self, analysis_results: Dict[str, Any]) -> float:
        """Evaluate overall cognitive capacity based on analysis results"""
        cognitive_capacity = 0.0
        factors = 0

        survival_analysis = analysis_results["survival_analysis"]
        learning_analysis = analysis_results["learning_analysis"]
        behavior_analysis = analysis_results["behavior_analysis"]
        if "learning_rate" in learning_analysis:
            # Normalized learning rate (expect values between -0.5 and 0.5)
            cognitive_capacity += min(1.0, max(0.0, (learning_analysis["learning_rate"] + 0.5) / 1.0))
            factors += 1

        if "adaptation_status" in behavior_analysis:
            # Add adaptation factor
            if behavior_analysis["adaptation_status"] == "still_adapting":
                cognitive_capacity += 0.8  # Still adapting is good
            else:
                environment_analysis = analysis_results["environment_analysis"]

                # Check if behavior is specialized appropriately
                if "environment_behavior_correlations" in environment_analysis:
                    # Higher correlations suggest appropriate specialization
                    avg_corr = np.mean([abs(v) for subdict in environment_analysis["environment_behavior_correlations"].values() 
                                       for v in subdict.values()])
                    cognitive_capacity += min(1.0, avg_corr * 2)  # Scale up, as correlations are often < 0.5
                    factors += 1

        if "energy_trends" in survival_analysis:
            # Add energy stability factor
            energy_stability = 1.0 - survival_analysis["energy_trends"]["std"]
            cognitive_capacity += energy_stability
            factors += 1

        return cognitive_capacity / factors if factors > 0 else 0
    
    def generate_comprehensive_report(self, simulation_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a comprehensive analysis report for a simulation"""
        if simulation_id is None:
            simulation_id = self.visualizer.get_latest_simulation_id()

        if simulation_id is None:
            return {"error": "No simulation logs found"}

        try:
            return self._extracted_from_generate_comprehensive_report_11(simulation_id)
        except Exception as e:
            return {"error": str(e)}

    # TODO Rename this here and in `generate_comprehensive_report`
    def _extracted_from_generate_comprehensive_report_11(self, simulation_id):
        # sourcery skip: low-code-quality
        # Load and analyze data
        analysis_results = self._load_and_analyze_data(simulation_id)
        df = analysis_results["df"]

        # Combine all analyses into a report
        report = {
            "simulation_id": simulation_id,
            "generated_at": datetime.now().isoformat(),
            "data_points": len(df),
            "start_iteration": df["iteration"].iloc[0],
            "end_iteration": df["iteration"].iloc[-1],
            "survival_analysis": analysis_results["survival_analysis"],
            "behavior_analysis": analysis_results["behavior_analysis"],
            "environment_analysis": analysis_results["environment_analysis"],
            "learning_analysis": analysis_results["learning_analysis"],
            "cluster_analysis": {
                "3_clusters": analysis_results["cluster_analysis_3"],
                "5_clusters": analysis_results["cluster_analysis_5"]
            }
        }

        # Generate final assessment
        assessment = {}
        survival_analysis = analysis_results["survival_analysis"]
        learning_analysis = analysis_results["learning_analysis"]
        behavior_analysis = analysis_results["behavior_analysis"]

        # Survival assessment
        if "energy_regression" in survival_analysis:
            energy_trend = survival_analysis["energy_regression"]["trend"]
            survival_trajectory = (
                "improving" if energy_trend == "increasing" else
                "critical" if energy_trend == "decreasing" and survival_analysis["energy_trends"]["final"] < 0.3 else
                "declining" if energy_trend == "decreasing" else
                "stable"
            )
            assessment["survival_trajectory"] = survival_trajectory

        # Learning assessment
        if "learning_category" in learning_analysis:
            assessment["learning_assessment"] = learning_analysis["learning_category"]

        # Behavioral assessment
        if "adaptation_status" in behavior_analysis:
            assessment["adaptation_status"] = behavior_analysis["adaptation_status"]
            assessment["behavior_strategy"] = (
                "specializing" if behavior_analysis["behavior_specialization"]["pattern"] == "specializing" 
                else "generalizing"
            )

        # Overall cognitive capacity assessment
        cognitive_capacity = self._evaluate_cognitive_capacity(analysis_results)

        capacity_category = (
            "exceptional" if cognitive_capacity > 0.8 else
            "high" if cognitive_capacity > 0.6 else
            "moderate" if cognitive_capacity > 0.4 else
            "limited" if cognitive_capacity > 0.2 else
            "primitive"
        )
        assessment["cognitive_capacity"] = capacity_category

        report["assessment"] = assessment
        return report
    
    def print_comprehensive_report(self, simulation_id: Optional[str] = None) -> None:
        """Print a comprehensive analysis report in a human-readable format"""
        report = self.generate_comprehensive_report(simulation_id)
        
        if "error" in report:
            print(f"Error generating report: {report['error']}")
            return
        
        print(f"\n{'='*80}")
        print(f"COGNITIVE SIMULATION ANALYSIS REPORT - {report['simulation_id']}")
        print(f"Generated: {report['generated_at']}")
        print(f"{'='*80}")
        
        print(f"\n{'-'*30} OVERVIEW {'-'*30}")
        print(f"Data points: {report['data_points']}")
        print(f"Iterations: {report['start_iteration']} to {report['end_iteration']}")
        
        # Print assessment
        if "assessment" in report:
            print(f"\n{'-'*30} ASSESSMENT {'-'*30}")
            for key, value in report["assessment"].items():
                print(f"{key.replace('_', ' ').title()}: {value.replace('_', ' ').title()}")
        
        # Print survival analysis
        if "survival_analysis" in report:
            print(f"\n{'-'*30} SURVIVAL ANALYSIS {'-'*30}")
            sa = report["survival_analysis"]
            
            if "energy_trends" in sa:
                print("Energy Trends:")
                for key, value in sa["energy_trends"].items():
                    if isinstance(value, float):
                        print(f"  {key}: {value:.2f}")
                    else:
                        print(f"  {key}: {value}")
            
            if "energy_regression" in sa:
                print("\nEnergy Trend Analysis:")
                er = sa["energy_regression"]
                print(f"  Trend: {er['trend']} ({er['significance']})")
                print(f"  Slope: {er['slope']:.4f}")
                print(f"  R-squared: {er['r_squared']:.4f}")
            
            if "correlations" in sa and sa["correlations"]:
                print("\nTop Energy Correlations:")
                for factor, corr in sa["correlations"][:5]:
                    print(f"  {factor}: {corr:.4f}")
        
        # Print behavior analysis
        if "behavior_analysis" in report:
            print(f"\n{'-'*30} BEHAVIOR ANALYSIS {'-'*30}")
            ba = report["behavior_analysis"]
            
            if "most_adapted_behaviors" in ba:
                print("Most Adapted Behaviors:")
                for behavior, change in ba["most_adapted_behaviors"][:3]:
                    print(f"  {behavior}: {change:.2f}% change")
            
            if "behavior_specialization" in ba:
                bs = ba["behavior_specialization"]
                print(f"\nBehavior Pattern: {bs['pattern']}")
                print(f"  Initial variance: {bs['initial_variance']:.4f}")
                print(f"  Final variance: {bs['final_variance']:.4f}")
            
            if "adaptation_status" in ba:
                print(f"\nAdaptation Status: {ba['adaptation_status'].replace('_', ' ').title()}")
        
        # Print learning analysis
        if "learning_analysis" in report:
            print(f"\n{'-'*30} LEARNING ANALYSIS {'-'*30}")
            la = report["learning_analysis"]
            
            if "learning_category" in la:
                print(f"Learning Category: {la['learning_category'].title()}")
            
            if "learning_rate" in la:
                print(f"Learning Rate: {la['learning_rate']:.4f}")
            
            if "learning_plateaus" in la and la["learning_plateaus"]:
                print(f"\nLearning Plateaus: {la['plateau_count']}")
                for i, plateau in enumerate(la["learning_plateaus"][:3]):
                    print(f"  Plateau {i+1}: Iterations {plateau['start_iteration']} to {plateau['end_iteration']}")
                    print(f"    Length: {plateau['length']} iterations")
                    print(f"    Efficiency: {plateau['efficiency_level']:.4f}")
        
        # Print operational modes (from cluster analysis)
        if "cluster_analysis" in report and "3_clusters" in report["cluster_analysis"]:
            print(f"\n{'-'*30} OPERATIONAL MODES {'-'*30}")
            
            modes = report["cluster_analysis"]["3_clusters"]["operational_modes"]
            for mode in modes:
                print(f"\nMode: {mode['name'].replace('_', ' ').title()}")
                print(f"  Size: {mode['size_percentage']:.1f}% of operations")
                
                for key, value in mode.items():
                    if key not in ["name", "size_percentage", "cluster"]:
                        print(f"  {key.replace('_', ' ').title()}: {str(value).replace('_', ' ').title()}")
        
        print(f"\n{'='*80}")
        print("END OF REPORT")
        print(f"{'='*80}\n")
    
    def plot_cluster_analysis(self, simulation_id: Optional[str] = None, 
                              n_clusters: int = 3, show: bool = True) -> None:
        """Visualize the cluster analysis results"""
        if simulation_id is None:
            simulation_id = self.visualizer.get_latest_simulation_id()

        if simulation_id is None:
            print("No simulation logs found.")
            return

        try:
            return self._extracted_from_plot_cluster_analysis_13(
                simulation_id, n_clusters, show
            )
        except Exception as e:
            print(f"Error plotting cluster analysis: {e}")
            return None

    # TODO Rename this here and in `plot_cluster_analysis`
    def _extracted_from_plot_cluster_analysis_13(self, simulation_id, n_clusters, show):
        # Prepare data for clustering
        df = self.load_simulation_data_as_df(simulation_id)
        result = self._prepare_cluster_data(df, n_clusters)

        if result is None:
            print("Not enough numerical data for clustering.")
            return

        num_cols, X_norm, pca, X_pca, kmeans, clusters = result

        # Create plots
        fig = plt.figure(figsize=(15, 10))

            # 3D plot if we have enough dimensions
        if X_pca.shape[1] >= 3:
            ax1 = fig.add_subplot(121, projection='3d')

            # Plot each cluster
            for i in range(n_clusters):
                ax1.scatter(
                    X_pca[clusters == i, 0],
                    X_pca[clusters == i, 1],
                    X_pca[clusters == i, 2],
                    label=f'Cluster {i}'
                )

            self._extracted_from_plot_cluster_analysis_38(
                ax1, '3D Cluster Visualization (PCA)', pca
            )
            ax1.set_zlabel(f'PC3 ({pca.explained_variance_ratio_[2]:.2%})')
            ax1.legend()

        # 2D plot
        ax2 = fig.add_subplot(122)

        # Create a time-colored scatter plot
        scatter = ax2.scatter(
            X_pca[:, 0],
            X_pca[:, 1],
            c=df["iteration"],
            cmap='viridis',
            alpha=0.7
        )

        # Add cluster centroids
        centroids = kmeans.cluster_centers_
        ax2.scatter(
            centroids[:, 0],
            centroids[:, 1],
            marker='X',
            s=200,
            c='red',
            label='Centroids'
        )

        # Add colorbar to show iteration progression
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('Iteration')

        self._extracted_from_plot_cluster_analysis_38(
            ax2, 'Behavioral States Over Time (PCA)', pca
        )
        ax2.legend()

        plt.suptitle(f'Cognitive Simulation: {simulation_id} - {n_clusters} Operational Modes')
        plt.tight_layout()

        if show:
            plt.show()

        return fig

    # TODO Rename this here and in `plot_cluster_analysis`
    def _extracted_from_plot_cluster_analysis_38(self, arg0, arg1, pca):
        arg0.set_title(arg1)
        arg0.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%})')
        arg0.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%})')


def main():
    """Run the advanced analysis on the latest simulation"""
    analyzer = CognitiveAnalysis()
    
    if latest_sim_id := analyzer.visualizer.get_latest_simulation_id():
        print(f"Analyzing latest simulation: {latest_sim_id}")
        analyzer.print_comprehensive_report(latest_sim_id)
        analyzer.plot_cluster_analysis(latest_sim_id)
    else:
        print("No simulation logs found.")

if __name__ == "__main__":
    main()