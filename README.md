# Torrent CLI

A command-line interface for searching and downloading torrents using Transmission.

## Installation

```bash
pip install torrent-cli
```

## Configuration

Before using the CLI, you need to configure your Transmission connection settings. By default, the CLI will try to connect to:
- Host: localhost
- Port: 9091
- Username: transmission
- Password: transmission

To change these settings, use the config command:

```bash
# Configure all settings at once
torrent-cli config --host your_host --port your_port --username your_username --password your_password

# Or configure individual settings
torrent-cli config --host your_host
torrent-cli config --username your_username
```

The configuration is stored in `~/.config/torrent-cli/config.json` and will be used for all future operations.

## Usage

Once you've configured your Transmission connection settings, you can start searching and downloading torrents:

```bash
torrent-cli "your search query"
```

The tool will:
1. Search for torrents matching your query
2. Display an interactive list of results with size, seeders, and leechers
3. Let you select which torrent to download using arrow keys
4. Add the selected torrent to your Transmission download queue

### Requirements

- Python 3.7+
- Transmission daemon running and accessible
- Proper authentication credentials for your Transmission server

### Example

```bash
# First, configure your Transmission settings
torrent-cli config --host 192.168.1.32 --port 9091 --username myuser --password mypass

# Then search for torrents
torrent-cli "ubuntu iso"
```

## Troubleshooting

If you encounter connection errors:
1. Verify your Transmission daemon is running
2. Check your configuration with `cat ~/.config/torrent-cli/config.json`
3. Ensure your Transmission credentials are correct
4. Confirm your Transmission daemon is accessible from your network
