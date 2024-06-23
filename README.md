# Dining Philosophers Simulator

## Project Overview

This project involves developing a simulator for the classic dining philosophers problem, a scenario used to study synchronization and deadlock issues in operating systems. Inspired by resource management challenges in concurrent environments, this project uses fundamental concepts of process synchronization as detailed in the context of Linux systems.

## Process Description

The philosophers, represented by processes or threads, spend their time alternating between eating and thinking. Each philosopher requires two forks to eat, located on either side of them at the table. The challenge is to develop an algorithm that allows each philosopher to eat without falling into a deadlock, while also avoiding starvation.

## Scheduling Policy Choices

Various strategies must be explored to avoid deadlocks and ensure that all philosophers can eat. These strategies include the server approach, where an arbitrator controls access to the forks, or ordered request strategies to avoid wait cycles.

## Expected Features

### Minimum Features

- **Philosophers Simulation**: Implement processes or threads that simulate the behavior of philosophers.
- **Concurrency Management**: Ensure that philosophers can access the forks without causing a deadlock.
- **Action Logging**: Record and display the actions of philosophers for analysis, such as when they eat, think, wait for forks, or put them down.

### Advanced Features

- **Graphical Visualization**: Develop a graphical interface to visualize the current state of the table, including the state of the philosophers and the availability of the forks.
- **Statistical Analysis**: Provide statistics on the number of times each philosopher has eaten and the average waiting time to eat.
- **Dynamic Strategies**: Allow users to change resource management strategies in real-time to compare their effectiveness.

## Deliverables

Each group must submit:

- **Source Code**: Complete, including simulation, concurrency management, and logging.
- **Makefile**: For compiling the program.

---

## Installation

To compile and run the simulator, follow the steps below:

1. Clone the repository:
   ```bash
   git clone https://github.com/Hamza-br/diner_des_philosophes
   cd diner_des_philosophes
   ```

2. Compile the program:
   ```bash
   make
   ```

3. Run the simulator:
   ```bash
   ./DINER
   ```

## Usage

Command-line options and configuration parameters will be documented here.

## Contributing

Contributions are welcome! Please submit pull requests and report issues via the GitHub issue tracker.

---

For any questions or comments, please contact [bourouhamza9@gmail.com](mailto:bourouhamza9@gmail.com).
