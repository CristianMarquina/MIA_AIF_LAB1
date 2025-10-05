# MIA_AIF_LAB1

This repository is for solving the problem from Lab 1 of the AIF course.

## Project Description

This project consists of the implementation and comparison of Artificial Intelligence search algorithms to solve a pathfinding problem. The objective is to find the minimum-cost path for a drilling robot from a starting point to a target location on a terrain with varying levels of hardness, respecting the robot's movement and orientation constraints.

The following algorithms are implemented and compared:

* **Blind Search**:

    * Breadth-First Search (BFS)
    * Depth-First Search (DFS)

* **Informed Search**:

    * A* (A-Star)

---

## Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites

Ensure you have the following installed:

* Python 3.8 or higher

### Installation

1.  **Clone the repository** to your local machine:
    ```bash
    git clone https://github.com/CristianMarquina/MIA_AIF_LAB1.git
    cd MIA_AIF_LAB1
    ```
2.  **Install dependencies**. This command reads the `requirements.txt` file and installs all the necessary libraries (`numpy` and `graphviz`) for the project to run.
    ```bash
    pip install -r requirements.txt
    ```
---

## Usage

The main script is executed from the command line, allowing you to specify the map file and the desired search algorithm.

### Command Structure

The general format for running a search is:
```bash
python main.py <map_path> -a <algorithm>