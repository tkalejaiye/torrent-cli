#!/usr/bin/env python3
import click
import requests
import inquirer
import os
import json
from pathlib import Path
from urllib.parse import quote
from transmission_rpc import Client

# Default configuration
DEFAULT_CONFIG = {
    "host": "localhost",
    "port": 9091,
    "username": "transmission",
    "password": "transmission"
}

def get_config():
    """Get configuration from config file or create default one."""
    config_dir = Path.home() / ".config" / "torrent-cli"
    config_file = config_dir / "config.json"
    
    if config_file.exists():
        with open(config_file) as f:
            return json.load(f)
    
    # Create default config if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    
    return DEFAULT_CONFIG

def search_torrents(query):
    """Search for torrents using the PirateBay API."""
    url = f"https://apibay.org/q.php?q={quote(query)}"
    response = requests.get(url)
    response.raise_for_status()
    
    torrents = response.json()
    # Take only the first 10 results
    return torrents[:10]

def format_size(size_bytes):
    """Convert size in bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def select_torrent(torrents):
    """Display an interactive prompt for torrent selection."""
    if not torrents:
        click.echo("No torrents found!")
        return None
        
    choices = [
        f"{t['name']} (Size: {format_size(int(t['size']))}, "
        f"Seeders: {t['seeders']}, Leechers: {t['leechers']})"
        for t in torrents
    ]
    
    questions = [
        inquirer.List('torrent',
                     message="Select a torrent to download",
                     choices=choices)
    ]
    
    answers = inquirer.prompt(questions)
    if not answers:
        return None
        
    # Find the selected torrent
    selected_index = choices.index(answers['torrent'])
    return torrents[selected_index]

def start_download(torrent):
    """Start downloading the selected torrent using Transmission."""
    # Get configuration
    config = get_config()
    
    # Connect to Transmission daemon
    client = Client(
        host=config["host"],
        port=config["port"],
        username=config["username"],
        password=config["password"]
    )
    
    # Create magnet link
    magnet = f"magnet:?xt=urn:btih:{torrent['info_hash']}&dn={quote(torrent['name'])}"
    
    # Add torrent to transmission
    client.add_torrent(magnet)
    click.echo("Successfully added torrent to download queue!")

def format_progress_bar(progress, width=30):
    """Create a progress bar string."""
    filled = int(width * progress)
    bar = "█" * filled + "-" * (width - filled)
    return f"[{bar}] {progress*100:.1f}%"

@click.group()
def cli():
    """Torrent CLI - Search and download torrents using Transmission."""
    pass

@cli.command()
@click.argument('query')
def search(query):
    """Search for torrents and download them using Transmission."""
    try:
        # Search for torrents
        torrents = search_torrents(query)
        
        # Let user select a torrent
        selected = select_torrent(torrents)
        if not selected:
            return
            
        # Start the download
        start_download(selected)
        
    except requests.RequestException as e:
        click.echo(f"Error searching for torrents: {e}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.option('--host', help='Transmission RPC host')
@click.option('--port', type=int, help='Transmission RPC port')
@click.option('--username', help='Transmission RPC username')
@click.option('--password', help='Transmission RPC password')
def config(host, port, username, password):
    """Configure Transmission connection settings."""
    config = get_config()
    
    if host:
        config["host"] = host
    if port:
        config["port"] = port
    if username:
        config["username"] = username
    if password:
        config["password"] = password
        
    config_file = Path.home() / ".config" / "torrent-cli" / "config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
    
    click.echo("Configuration updated successfully!")

@cli.command()
def queue():
    """View all torrents in the Transmission queue with their status."""
    config = get_config()
    
    try:
        client = Client(
            host=config["host"],
            port=config["port"],
            username=config["username"],
            password=config["password"]
        )
        
        torrents = client.get_torrents()
        
        if not torrents:
            click.echo("No torrents in queue!")
            return
            
        for torrent in torrents:
            status = torrent.status
            name = torrent.name
            
            # Display basic info
            click.echo(f"\n{name}")
            click.echo(f"Status: {status}")
            
            # Show progress for downloading torrents
            if status == "downloading":
                progress = torrent.progress / 100.0
                speed = format_size(torrent.rate_download) + "/s"
                progress_bar = format_progress_bar(progress)
                click.echo(f"Progress: {progress_bar}")
                click.echo(f"Download Speed: {speed}")
            
            # Show other relevant information
            size = format_size(torrent.total_size)
            click.echo(f"Size: {size}")
            
    except Exception as e:
        click.echo(f"Error connecting to Transmission: {str(e)}")

main = cli

if __name__ == '__main__':
    main()
