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
Configure your experiments before you execute the shell files to start them:

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
### Native `config.json`
Same structure, without the `netem` section:

```json
{
  "host": "127.0.0.1",
  "port": 8443,
  "handshake_runs": 1000,
  "mode": {
    "selected": "hybrid",
    "classic": "x22519",
    "pqc": "Kyber768",
    "hybrid": {
      "classic": "x22519",
      "pqc": "Kyber768"
    }
  },
  "logs": {
    ...
    }
  }
}
```

## Running the Experiments
To run all modes (classical, post-quantum, hybrid):
 ```bash
 cd kex-native
 bash run_all_enc_modes.sh
```

> or to just run the configured mode (Docker only):
 ```bash
 cd kex-native
 bash restart_experiment.sh
```

> Metrics recorded will be saved to `{kex-native, kex-docker}logs/{classic,pqc,hybrid}/` as CSV files.

## Data

Navigate to `analytics/notebooks/`:

- `01_transport_data.ipynb`: Transfers raw logs from native/docker environments to the analysis folder.
- `02_parsing_and_exploration.ipynb`: Parses and explores the performance metrics.

## Preconducted experiments
5 experiments were conducted with various network profiles (defined in config file) on two different devices:

> MacBook Pro (Model Mac16,8), Apple M4 Pro, 12-core CPU 24 GB unified memory 
Find measurement data as `all_measurements_macbook.csv`
> Raspberry Pi 4 Model B Rev 1.1
Find measurement data as `all_measurements_raspberry.csv`

## Supported Key Exchange Modes
- **Classic** - ECDH x25519
- **Post-quantum** - Kyber768
- **Hybrid** - x25519_Kyber768

