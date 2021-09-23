# Extract data from Trello using API

Script to extract summary of recent (last 8 days') card moves from a Trello board.

## Usage

Run `python extract_recent.py [TRELLO KEY] [TRELLO TOKEN] [BOARD ID]`.

## Setup

1. `git clone https://github.com/ahernp/trello.git`
1. `cd trello`
1. `python3 -m venv venv` Create Python 3 virtual environment.
1. `source venv/bin/activate` Activate Python virtual environment.
1. `pip install py-trello`

