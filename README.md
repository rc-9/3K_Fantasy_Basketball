[![Issues][issues-shield]][issues-url]


<h1 align="center">NBA 3K</h1>
<h3 align="center">Fantasy Basketball Virtual Assistant</h3>
<p align="center">
    Troy J., Adi B., Romith C.
    <br /><br />
    <a href="https://github.com/rc-9/3K_Fantasy_Basketball/issues">Report Bug</a>
    ·
    <a href="https://github.com/rc-9/3K_Fantasy_Basketball/issues">Request Feature</a>
    <br /><br />
    <a href="https://a1.espncdn.com/combiner/i?img=%2Fi%2Fespn%2Fmisc_logos%2F500%2Ffba.png">
        <img src="https://a1.espncdn.com/combiner/i?img=%2Fi%2Fespn%2Fmisc_logos%2F500%2Ffba.png" alt="ESPN NBA Logo" />
    </a>
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

