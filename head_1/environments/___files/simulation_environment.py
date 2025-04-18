import random
import time
import threading
from collections import defaultdict

class SimulationEnvironment:
    """
    A robust and versatile simulation environment designed to model and analyze artificial lifeforms and their interactions within a complex system.

    This environment is capable of:
    - Self-containment: Operating independently with minimal external dependencies.
    - Metriculation: Tracking and recording a wide range of performance metrics.
    - Analysis: Providing tools and methods for analyzing the collected data.
    - Tracking: Monitoring the state and behavior of all entities within the simulation.
    - Handling diverse complexities: Supporting simple on/off code to advanced cognitive intelligence.
    - Managing multiple interconnected programs: Facilitating interactions between different AI systems.
    - Preventing logical failures: Robust architecture to ensure continuous and reliable operation.

    The environment includes intelligent systems for generating obstacles, rewards, and other dynamic elements,
    creating a challenging and engaging simulation for the artificial lifeforms.
    """
    def __init__(self, size=(100, 100), initial_resources=1000, complexity_level="medium", name="Alife_Simulation"):
        """
        Initializes the simulation environment.

        Args:
            size (tuple): The dimensions of the environment (width, height).  Defaults to (100, 100).
            initial_resources (int): The starting amount of resources in the environment. Defaults to 1000.
            complexity_level (str):  "basic", "medium", or "advanced".  Controls environment dynamics.
            name (str): Name of the simulation.
        """
        self.size = size
        self.width, self.height = size  # Unpack for easier use
        self.grid = [[None for _ in range(self.height)] for _ in range(self.width)]  # Use size
        self.time = 0
        self.running = False
        self.entities = {}  # Store entities using a unique ID
        self.resources = initial_resources
        self.global_metrics = defaultdict(list)  # Store global metrics over time
        self.complexity_level = complexity_level  # Store complexity
        self.name = name
        self.event_log = []  # Store significant events
        self.lock = threading.Lock() #prevent race conditions

        # Environment dynamics settings (Intelligent Obstacles, Rewards, etc.)
        self.obstacle_density = 0.1 if complexity_level in ["medium", "advanced"] else 0.01
        self.reward_density = 0.05 if complexity_level in ["medium", "advanced"] else 0.02
        self.resource_replenishment_rate = 0.02 if complexity_level == "advanced" else 0.01  # as a fraction of resources
        self.dynamic_events = True if complexity_level == "advanced" else False # Whether to have random events
        self.agent_capacity = 100 if complexity_level in ["medium", "advanced"] else 10 #max agents
        self. программы = {} #handles multiple programs

        self._initialize_environment()  # Initialize the environment when the object is created

    def _initialize_environment(self):
        """
        Initializes the environment with static elements such as obstacles and initial resources.
        """
        self.event_log.append({"time": self.time, "event": "Environment Initialized"})
        # Create obstacles
        num_obstacles = int(self.width * self.height * self.obstacle_density)
        for _ in range(num_obstacles):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            if self.grid[x][y] is None:  # Prevent overwriting
                self.grid[x][y] = "Obstacle"
                self.event_log.append({"time": self.time, "event": f"Obstacle created at ({x}, {y})"})

        # Distribute initial resources
        # Resources are not tied to specific grid locations, but are a global amount.
        self.event_log.append({"time": self.time, "event": f"Initial resources set to {self.resources}"})

    def add_entity(self, entity):
        """
        Adds an entity to the simulation environment.

        Args:
            entity (BaseEntity): The entity to add.  Must inherit from BaseEntity.

        Raises:
            TypeError: If the entity is not an instance of BaseEntity.
            Exception: If the entity's ID already exists or if the environment is full.
        """
        from .entities import BaseEntity  # Import here to avoid circular dependency
        if not isinstance(entity, BaseEntity):
            raise TypeError("entity must be an instance of BaseEntity")

        with self.lock: #use lock
            if entity.id in self.entities:
                raise Exception(f"Entity with ID {entity.id} already exists.")
            if len(self.entities) >= self.agent_capacity:
                raise Exception("Environment is at maximum agent capacity.")
            self.entities[entity.id] = entity
            self.event_log.append({"time": self.time, "event": f"Entity {entity.id} added at ({entity.x}, {entity.y})"})
            self.grid[entity.x][entity.y] = entity #place entity on grid

    def remove_entity(self, entity_id):
        """
        Removes an entity from the simulation environment.

        Args:
            entity_id (str): The ID of the entity to remove.
        """
        with self.lock: #use lock
            if entity_id not in self.entities:
                # Log the error, but don't raise an exception.  The simulation should continue.
                self.event_log.append({"time": self.time, "event": f"Error: Entity with ID {entity_id} not found for removal."})
                return
            entity = self.entities[entity_id]
            self.grid[entity.x][entity.y] = None #remove from grid
            del self.entities[entity_id]
            self.event_log.append({"time": self.time, "event": f"Entity {entity_id} removed"})

    def get_entity_position(self, entity_id):
        """
        Retrieves the position of an entity in the environment.

        Args:
            entity_id (str): The ID of the entity.

        Returns:
            tuple: The (x, y) coordinates of the entity, or None if the entity is not found.
        """
        with self.lock:
            if entity_id in self.entities:
                entity = self.entities[entity_id]
                return entity.x, entity.y
            else:
                return None

    def move_entity(self, entity_id, new_x, new_y):
        """
        Moves an entity to a new location in the environment.

        Args:
            entity_id (str): The ID of the entity to move.
            new_x (int): The new x-coordinate.
            new_y (int): The new y-coordinate.

        Raises:
            ValueError: If the new coordinates are out of bounds.
            Exception: If there is an obstacle or another entity at the new location.
        """
        with self.lock:
            if entity_id not in self.entities:
                raise Exception(f"Entity with ID {entity_id} not found for movement.")

            entity = self.entities[entity_id]
            if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                raise ValueError("New coordinates are out of bounds.")

            if self.grid[new_x][new_y] is not None and self.grid[new_x][new_y] != "Obstacle":
                raise Exception(f"Cannot move entity {entity_id} to ({new_x}, {new_y}): Location is occupied.")

            #update grid
            self.grid[entity.x][entity.y] = None
            self.grid[new_x][new_y] = entity
            entity.x = new_x
            entity.y = new_y
            self.event_log.append({"time": self.time, "event": f"Entity {entity_id} moved to ({new_x}, {new_y})"})

    def get_neighbors(self, x, y, radius=1):
        """
        Retrieves neighboring entities within a specified radius.  Includes obstacles.

        Args:
            x (int): The x-coordinate of the center location.
            y (int): The y-coordinate of the center location.
            radius (int): The radius of the neighborhood.  Defaults to 1.

        Returns:
            list: A list of entities (or "Obstacle" strings) within the radius.
                   Returns empty list if x,y is out of bounds.
        """
        neighbors = []
        if not (0 <= x < self.width and 0 <= y < self.height):
            return neighbors #return empty list

        for i in range(max(0, x - radius), min(self.width, x + radius + 1)):
            for j in range(max(0, y - radius), min(self.height, y + radius + 1)):
                if (i, j) != (x, y):  # Exclude the center location
                    if self.grid[i][j] is not None:
                        neighbors.append(self.grid[i][j])
                    else:
                        neighbors.append(None) # Add None for empty spots
        return neighbors

    def get_resource_amount(self):
        """
        Retrieves the current amount of resources in the environment.

        Returns:
            int: The current resource amount.
        """
        return self.resources

    def consume_resources(self, amount):
        """
        Consumes resources from the environment.

        Args:
            amount (int): The amount of resources to consume.

        Raises:
            ValueError: If the amount is negative.
            Exception: If there are insufficient resources.
        """
        if amount < 0:
            raise ValueError("Resource consumption amount cannot be negative.")
        with self.lock:
            if self.resources < amount:
                raise Exception("Insufficient resources.")
            self.resources -= amount
            self.event_log.append({"time": self.time, "event": f"{amount} resources consumed"})

    def replenish_resources(self):
        """
        Replenishes resources in the environment based on the replenishment rate.
        """
        with self.lock:
            replenishment = int(self.resources * self.resource_replenishment_rate)
            self.resources += replenishment
            self.event_log.append({"time": self.time, "event": f"{replenishment} resources replenished"})

    def update_global_metrics(self):
        """
        Updates global metrics for the simulation, such as total energy consumption,
        average fitness, etc.  This is called every time step.
        """
        total_energy = 0
        num_entities = 0
        total_fitness = 0

        with self.lock:  # Ensure thread-safe access to entity data.
            for entity in self.entities.values():
                total_energy += entity.energy
                num_entities += 1
                total_fitness += entity.fitness  # Assuming each entity has a 'fitness' attribute

            if num_entities > 0:
                avg_fitness = total_fitness / num_entities
            else:
                avg_fitness = 0

            self.global_metrics["time"].append(self.time)
            self.global_metrics["total_energy"].append(total_energy)
            self.global_metrics["num_entities"].append(num_entities)
            self.global_metrics["avg_fitness"].append(avg_fitness)
            self.global_metrics["resources"].append(self.resources) #track resources

    def introduce_dynamic_events(self):
        """
        Introduces random dynamic events into the simulation, such as sudden resource influx,
        environmental disasters, or the appearance of new entities.  Only in "advanced" mode.
        """
        if not self.dynamic_events:
            return  # Only execute if dynamic events are enabled.

        event_chance = 0.05  # 5% chance of an event occurring each time step.
        if random.random() < event_chance:
            event_type = random.choice(["resource_influx", "environmental_disaster", "new_entities"])
            with self.lock:
                if event_type == "resource_influx":
                    influx_amount = int(self.resources * 0.2)  # 20% increase
                    self.resources += influx_amount
                    self.event_log.append({"time": self.time, "event": f"Resource influx of {influx_amount}!"})
                elif event_type == "environmental_disaster":
                    # பாதி = destruction
                    destruction_amount = int(len(self.entities) * 0.3)  # Destroy 30% of entities
                    if destruction_amount > 0:
                        entities_to_destroy = random.sample(list(self.entities.keys()), destruction_amount)
                        for entity_id in entities_to_destroy:
                            self.remove_entity(entity_id)  # Use the remove_entity method
                        self.event_log.append({"time": self.time, "event": f"Environmental disaster! {destruction_amount} entities destroyed."})
                elif event_type == "new_entities":
                    from .entities import SimpleEntity # Import here to avoid circular dependency
                    num_new_entities = random.randint(1, 5)
                    for _ in range(num_new_entities):
                        #find a random empty spot
                        x = random.randrange(self.width)
                        y = random.randrange(self.height)
                        if self.grid[x][y] is None:
                            new_entity = SimpleEntity(id=f"new_entity_{self.time}_{random.randint(1,1000)}", x=x, y=y, energy=50)
                            self.add_entity(new_entity)
                    self.event_log.append({"time": self.time, "event": f"{num_new_entities} new entities appeared."})

    def run_simulation(self, num_iterations=1000, time_step=0.1):
        """
        Runs the simulation for a specified number of iterations.

        Args:
            num_iterations (int): The number of iterations to run. Defaults to 1000.
            time_step (float): The time increment for each iteration (in seconds). Defaults to 0.1.
        """
        if self.running:
            print("Simulation is already running.")
            return

        self.running = True
        self.event_log.append({"time": self.time, "event": "Simulation started"})
        for _ in range(num_iterations):
            if not self.running:
                break #stop if not running
            self.time += time_step

            # 1. Update environment (obstacles, rewards, resource replenishment)
            self.update_environment()

            # 2. Update entities (move, interact, consume energy)
            with self.lock: #iterate through a copy
                for entity_id in list(self.entities.keys()):
                    entity = self.entities[entity_id] #get entity
                    entity.update(self)  # Pass the entire simulation environment
                    if not entity.alive: #check if entity is alive
                        self.remove_entity(entity_id)

            # 3. Replenish resources
            self.replenish_resources()

            # 4. Update global metrics
            self.update_global_metrics()

            # 5. Introduce dynamic events (if applicable)
            self.introduce_dynamic_events()

            time.sleep(time_step)  # Simulate real-time behavior

        self.running = False
        self.event_log.append({"time": self.time, "event": "Simulation ended"})

    def update_environment(self):
        """
        Updates the environment.  This method is designed to be overridden
        in derived classes to implement specific environment dynamics.
        """
        # Example: Introduce a small chance of new obstacle appearing
        if random.random() < 0.01:  # 1% chance
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            if self.grid[x][y] is None:
                self.grid[x][y] = "Obstacle"
                self.event_log.append({"time": self.time, "event": f"New obstacle created at ({x}, {y})"})

        # Example:  Introduce a small chance of a reward appearing
        if random.random() < 0.02: # 2% chance
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            if self.grid[x][y] is None:
                self.grid[x][y] = "Reward"  # Use a string or a Reward object
                self.event_log.append({"time": self.time, "event": f"New reward created at ({x}, {y})"})

    def get_grid_state(self):
        """
        Returns a copy of the current state of the grid.  Used for visualization or analysis.
        Returns a 2D list where each element is either None, "Obstacle", an entity, or "Reward"
        """
        grid_copy = [[None for _ in range(self.height)] for _ in range(self.width)]
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y] is None:
                    grid_copy[x][y] = None
                elif self.grid[x][y] == "Obstacle":
                    grid_copy[x][y] = "Obstacle"
                elif isinstance(self.grid[x][y], BaseEntity):
                    grid_copy[x][y] = self.grid[x][y].id #store the id
                elif self.grid[x][y] == "Reward":
                    grid_copy[x][y] = "Reward"
                else:
                    grid_copy[x][y] = "Unknown"
        return grid_copy

    def get_global_metrics(self):
        """
        Returns the global metrics dictionary.
        """
        return self.global_metrics

    def get_event_log(self):
        """
        Returns the event log.
        """
        return self.event_log

    def add_program(self, program_name, program_instance):
        """
        Adds a program to the simulation.  This allows for running multiple
        concurrent programs within the simulation environment.
        """
        with self.lock:
            if program_name in self.programs:
                raise ValueError(f"Program named '{program_name}' already exists.")
            self.programs[program_name] = program_instance
            self.event_log.append({"time": self.time, "event": f"Program '{program_name}' added."})

    def get_program(self, program_name):
        """
        Retrieves a program from the simulation.
        """
        with self.lock:
            if program_name not in self.programs:
                return None
            return self.programs[program_name]

    def remove_program(self, program_name):
        """
        Removes a program from the simulation.
        """
        with self.lock:
            if program_name not in self.programs:
                self.event_log.append({"time": self.time, "event": f"Error: Program '{program_name}' not found for removal."})
                return #dont raise error, just log
            del self.programs[program_name]
            self.event_log.append({"time": self.time, "event": f"Program '{program_name}' removed."})

    def run_program(self, program_name, *args, **kwargs):
        """
        Runs a program within the simulation.  This uses a thread to allow
        the simulation to continue running while the program executes.
        """
        program = self.get_program(program_name)
        if program is None:
            raise ValueError(f"Program '{program_name}' not found.")
        thread = threading.Thread(target=program.run, args=args, kwargs=kwargs)
        thread.start()
        self.event_log.append({"time": self.time, "event": f"Program '{program_name}' started in a new thread."})

    def stop_simulation(self):
        """
        Stops the simulation.
        """
        self.running = False
        self.event_log.append({"time": self.time, "event": "Simulation stopped."})

    def __str__(self):
        """
        Returns a string representation of the simulation environment.
        """
        return f"SimulationEnvironment(name='{self.name}', size={self.size}, time={self.time}, running={self.running}, num_entities={len(self.entities)}, resources={self.resources}, complexity={self.complexity_level})"

    def __repr__(self):
        """
        Official string representation for developers (useful for debugging).
        """
        return f"SimulationEnvironment(name={self.name!r}, size={self.size!r}, time={self.time!r}, running={self.running!r}, entities={self.entities!r}, resources={self.resources!r}, complexity_level={self.complexity_level!r})"
