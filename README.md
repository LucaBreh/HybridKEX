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

 > If you're running the project natively, install the required Python packages with:

 ```bash
 pip install -r requirements.txt
 ```

## Configuration
Each environment uses its own `config.json` in the `shared/` directory.

### Docker `config.json`
Includes support for **network emulation**:

```json
{
  "host": "server",
  "port": 8443,
  "handshake_runs": 1000,
  "mode": {
    "selected": "pqc",
    "classic": "x22519",
    "pqc": "Kyber768",
    "hybrid": {
      "classic": "x22519",
      "pqc": "Kyber768"
    }
  },
  "time_digits": 10,
  "logs": {
    ...
    }
  },
  "netem": {
    "enabled": false,
    "selected": "netem_satelite",
    ... # predefined network profiles
  }
}
```


## Running the Experiments
 ```bash
 cd kex-native
```






