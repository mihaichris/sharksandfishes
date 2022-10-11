# SharksAndFishes - Conways Game of Life

## Description
Parallel implementation of Conway's Game of Life using Python MPI library.

## Basic Usage
To run the project use:

```python
python -m sharksandfishes
```
## About Sharks and Fishes problem

A very popular simulator, derived from the notion of cell automata, is "Sharks and fish" in the sea, each having a different behavior. The problem was conceived by Alexander Keewatin Dewdney and presented in the scientific article "Computer Recreations: Sharks and Fish Lead an Environmental War on the Toroidal Planet Wa-Tor". It's a simulator where you have two species of creatures, fish and sharks, each with a role in this world.

## Rules

Every advance in this world is called in the form of a generation. In every generation, every state of a creature evolves according to certain rules and criteria. It moves to a certain position in the space in which they live, if that cell is not occupied by another creature of the same species. This position selection process is random:

* Fish rules:
  * If it is a free adjacent cell, the fish goes to that cell;
  * If there are several adjacent cells free, the fish chooses one cell at random;
  * If there are no loose cells around, the fish is standing still;
  * If the fish has reached the breeding age, it gives rise to another small fish that is left in the vacant cell;
  * The fish dies after a finite number of generations;
  
* Shark rules:
  * If an adjacent cell is occupied by a fish, the shark goes to that cell and eats the fish;
  * If cells adjacent to the shark are occupied by several fish, at that point the shark goes to a cell in a random way and eats the fish;
  * If there is no fish in the cells adjacent to the shark, it will choose an adjacent cell that is empty, in the same way as the fish;
  * If the shark has reached the breeding age, it gives rise to another small shark that is left in the vacant cell;
  * If the shark has not eaten for a finite number of generations, it will die;
  
* Possible results:
  * A perfect balance between fish and sharks, their number increasing and decreasing but never exterminating a species;
  * Disappearance of sharks;
  * The extermination of both species;
