[![Issues][issues-shield]][issues-url]


<h1 align="center">3K: Fantasy Basketball Virtual Assistant</h1>
  <p align="center">
    Troy J., Adi B., Romith C.
    <br />
    <br />
    <a href="https://github.com/rc-9/3K_Fantasy_Basketball/issues">Report Bug</a>
    ·
    <a href="https://github.com/rc-9/3K_Fantasy_Basketball/issues">Request Feature</a><br />
    <br><a href="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSAJn3M_b31v-g2wAm3b5mrWon81HSM1dyP3w&usqp=CAU"><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSAJn3M_b31v-g2wAm3b5mrWon81HSM1dyP3w&usqp=CAU" alt="z3" border="" /></a><br />
    Image Source: saurabhr.com
</p>
</div>


## About The Project

The purpose of this project is to build an end-to-end, data-driven fantasy basketball assistant that automates daily decisions involving lineup selection, waiver wire pickups, and trade targets.

## Usage

- ```execute_cleaners.py```: Executes a series of data engineering steps by calling upon helper modules. 
    - Raw data files are located within `data/raw`. Processed files are saved to `data/processed`. Helper cleaner modules are in the `cleaners` directory.
- ```hot_streak_finder.py```: Implements a divide-and-conquer algorithm to discover seasonal patterns in player performance, in order to aid fantasy users in waiver-wire decisions.
  - Calls upon helper modules in `utils`.
- ```fantasy_trades_cluster_analysis.py```: Explores the applicability & potency of unsupervised algorithms in building a strategic fantasy draft tool.
- ```tests```: Contains the unit-tests for all the scripts.

<!-- MARKDOWN LINKS & IMAGES -->
[issues-shield]: https://img.shields.io/github/issues/rc-9/3K_Fantasy_Basketball.svg?style=for-the-badge
[issues-url]: https://github.com/rc-9/3K_Fantasy_Basketball/issues

