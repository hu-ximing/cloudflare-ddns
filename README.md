# Cloudflare DDNS

This project sets up a cron job that runs the `dns_updater.py` script every 30 minutes to check and update the DNS record if the public IP address has changed.

This script uses the [Cloudflare API](https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-update-dns-record) to update a dynamic IP address for a specified DNS record.

## Prerequisites

- A Cloudflare account with an API token
- A Cloudflare zone ID
- A record name (domain name)

## Setup

1. Clone the repository:

    ```sh
    git clone https://github.com/hu-ximing/cloudflare-ddns
    cd cloudflare-ddns
    ```

2. Rename `config.example.json` to `config.json`:

    ```sh
    mv config.example.json config.json
    ```

3. Edit the `config.json` file and fill in your Cloudflare API token, zone ID, and record name:

    ```json
    {
        "api_token": "your_api_token",
        "zone_id": "your_zone_id",
        "record_name": "example.com"
    }
    ```

4. Run `setup.sh` to register script in cron

    ```sh
    sh setup.sh
    ```

    If you need to change the directory location, make sure to update the cron job accordingly.  
    To edit the cron job, run `crontab -e`

## Files

- `dns_updater.py`: The main script that interacts with the Cloudflare API.

- `config.example.json`: Config file with empty Cloudflare credentials.

- `setup.sh`: Script to set up python venv, cron job and logging

## How to Find Your Cloudflare API Token and Zone ID

### To get your API Token

1. Log in to your [Cloudflare dashboard](https://dash.cloudflare.com/)

2. Click your profile icon in the top right

3. Go to "My Profile"

4. Select "API Tokens" from the left sidebar

5. Click "Create Token" or use an existing one

    - You can use the "Edit zone DNS" template for DNS management

    - Or create a custom token with specific permissions

6. Copy the generated API token and use it in your `config.json` file.

### To find your Zone ID

1. Log in to your [Cloudflare dashboard](https://dash.cloudflare.com/)

2. Select the domain/website you want to work with

3. Go to the "Overview" tab

4. Scroll down - your Zone ID will be listed on the right side under "API" section

5. Copy Zone ID and use it in your `config.json` file.

## License

This code is released into the public domain.
