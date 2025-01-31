import requests
import os
from pathlib import Path
import json
from datetime import datetime

script_dir = Path(__file__).resolve().parent


def log(msg):
    # Print log message to console and write to log file
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{current_time}] {msg}\n"
    print(log_entry, end="")

    os.makedirs(f"{script_dir}/logs", exist_ok=True)
    with open(f"{script_dir}/logs/dns_updater.log", "a") as f:
        f.write(log_entry)


def get_cached_ip(ip_cache_file):
    # Read the last known IP from cache file
    try:
        if os.path.exists(ip_cache_file):
            with open(ip_cache_file, "r") as f:
                return f.read().strip()
    except Exception as e:
        log(f"Error reading cache: {str(e)}")
    return None


def update_cached_ip(ip_cache_file, ip):
    # Update the cached IP
    try:
        with open(ip_cache_file, "w") as f:
            f.write(ip)
    except Exception as e:
        log(f"Error updating cache: {str(e)}")


def get_public_ip():
    # Get public IP address using HTTP request
    try:
        response = requests.get("http://1.1.1.1/cdn-cgi/trace")
        if response.status_code == 200:
            # Parse the response text to find IP
            for line in response.text.splitlines():
                if line.startswith("ip="):
                    return line.split("=")[1]
        return None
    except requests.RequestException as e:
        log(f"Error getting IP via HTTP: {e}")
        return None


def get_dns_record_id(base_url, headers, zone_id, record_name):
    # Get DNS record ID from Cloudflare
    try:
        url = f"{base_url}/zones/{zone_id}/dns_records"
        params = {"name": record_name}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        records = response.json()["result"]
        return records[0]["id"] if records else None
    except requests.RequestException as e:
        log(f"Error getting DNS record: {str(e)}")
        return None


def update_dns_record(base_url, headers, zone_id, record_id, record_name, new_ip):
    # Update DNS record with new IP
    try:
        url = f"{base_url}/zones/{zone_id}/dns_records/{record_id}"
        data = {"type": "A", "name": record_name, "content": new_ip, "proxied": True}

        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()

        return response.json()["success"]
    except requests.RequestException as e:
        log(f"Error updating DNS record: {str(e)}")
        return False


def update_ddns(api_token, zone_id, record_name):
    # Main function to check and update IP if needed
    base_url = "https://api.cloudflare.com/client/v4"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    ip_cache_file = f"{script_dir}/current_ip.txt"

    try:
        current_ip = get_cached_ip(ip_cache_file)
        new_ip = get_public_ip()

        if new_ip and new_ip != current_ip:
            log(f"IP change detected: {current_ip} -> {new_ip}")

            record_id = get_dns_record_id(base_url, headers, zone_id, record_name)
            if record_id:
                if update_dns_record(
                    base_url, headers, zone_id, record_id, record_name, new_ip
                ):
                    log(f"Successfully updated DNS record to {new_ip}")
                    update_cached_ip(ip_cache_file, new_ip)
                else:
                    log("Failed to update DNS record")
            else:
                log("Could not find DNS record ID")
        else:
            log("No IP change detected")

    except Exception as e:
        log(f"Unexpected error: {str(e)}")


def load_config(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    # Load configuration from config.json
    config_file = Path(__file__).resolve().parent / "config.json"
    config = load_config(config_file)

    api_token = config["api_token"]
    zone_id = config["zone_id"]
    record_name = config["record_name"]

    if not all([api_token, zone_id, record_name]):
        print("Please set required configuration in config.json:")
        print("api_token, zone_id, record_name")
        exit(1)

    update_ddns(api_token, zone_id, record_name)
