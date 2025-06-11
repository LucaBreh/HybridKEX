# KEX Benchmarking Framework
## Project Overview
This project provides a testing framework for evaluation key exchange (KeX) mechanisms - **classic**, **post-quantum**, and **hybrid** - in both native and Docker-based environments. It enables automated, repeatable experiments to benchmark KEX performance under various configuratins and network conditions.

## Project Structure

```
├── README.md
├── analytics               # Data storage, analysis, and visualization
│   ├── data/               # Preceding experiments on a MacBook and a RaspberryPi
│   └── notebooks/          # Data parsing, analyisis, and visualization
│
├── kex-docker              # Docker-based experiment setup
│   ├── client/             # Client-side implementation
│   ├── server/             # Server-side implementation
│   ├── shared/             # Shared crypto logic and config
│   ├── logs                # Log files for all KEX modes
│   └── *.sh                # Shell scripts to run and manage exeriments
│
└── kex-native              # Native (non-containerized) experiment setup
    ├── logs                # Log files for all KEX modes
    ├── shared/             # Shared crypto logic and config
    └── *.py / *.sh         # Native Python scripts and launchers
```

## Getting Started

## Requirements
 - Python 3.11
 - Docker & Docker Compose








