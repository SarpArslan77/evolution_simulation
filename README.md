# Ecological Simulation Project

Welcome to the Ecological Simulation Project repository! This project is a Python-based simulation that models the interactions between various biological entities within a dynamic ecosystem. The simulation aims to explore the behaviors and life cycles of different organisms as they interact with each other and their environment.

## Overview

The simulation includes several types of entities, each represented by a specific Python class:
- **Predator Cells**: These entities simulate predatory behavior, seeking out and consuming other cells to survive.
- **Producer Cells**: These cells are capable of producing food resources within the environment, contributing to the energy flow in the ecosystem.
- **Saprophytes**: Organisms that specialize in consuming decomposing organic matter, playing a crucial role in nutrient recycling.
- **Shit**: Represents decomposable material left by other organisms, which can be consumed by saprophytes.
- **Food**: Basic units of nutrition that can be consumed by various organisms to gain energy.

Each class handles specific behaviors such as movement, reproduction, aging, and interactions with other entities and the environment, providing a rich simulation of ecological dynamics.

## Project Structure

The project is organized into several modules, each responsible for different aspects of the simulation:
- `general.py`: Defines the `General` class, which sets up and manages the global properties of the simulation environment, such as world dimensions and environmental settings.
- `predator_cell.py`: Contains the `Predator_Cell` class, detailing the behaviors and properties of predatory organisms.
- `producer_cell.py`: Implements the `Producer_Cell` class, which manages the life cycle and food production capabilities of producer organisms.
- `saprophyte.py`: Hosts the `Saprophyte` class, responsible for the behaviors of organisms that consume decomposing material.
- `utility.py`: Includes utility classes like `Shit` and `Food`, which represent non-living elements within the ecosystem that interact with the living organisms.

## Features

- **Dynamic Ecosystem**: The simulation models a complex ecosystem where entities interact based on predefined and emergent behaviors, influencing each other's survival and reproduction.
- **Genetic Variation and Mutation**: Organisms possess genetic traits that influence their behaviors and efficiency. These traits can undergo mutations, leading to variations in the population over time.
- **Environmental Impact**: The environment affects the life cycles of organisms, with factors such as resource availability and competition playing critical roles.
- **Lifecycle Management**: Each entity type follows a lifecycle that includes birth, growth, reproduction, and death, influenced by individual genetic traits and environmental conditions.
