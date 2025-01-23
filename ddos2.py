import re
import geoip2.database
import json

def extract_unique_ips(log_file_path):
    with open(log_file_path, 'r') as file:
        log_content = file.read()

    # extract chrome useragent
    log_pattern = r'(\d+\.\d+\.\d+\.\d+) - - \[.*\] "GET .*" \d+ \d+ ".*" ".*Chrome\/(\d+)\.\d+\.\d+\.\d+.*"'
    matches = re.findall(log_pattern, log_content)

    # filter string where chrome < 110
    filtered_ips = [ip for ip, chrome_version in matches if int(chrome_version) < 110]

    unique_ips = set(filtered_ips)
    return unique_ips

def is_private_ip(ip):
    """
    check local networks
    """
    # split octets
    octets = list(map(int, ip.split('.')))

    # 10.0.0.0/8
    if octets[0] == 10:
        return True

    # 172.16.0.0/12
    if octets[0] == 172 and 16 <= octets[1] <= 31:
        return True

    # 192.168.0.0/16
    if octets[0] == 192 and octets[1] == 168:
        return True

    # if not locals than it's internet
    return False

def get_country_by_ip(ip, reader):
    try:
        response = reader.country(ip)
        return response.country.iso_code
    except geoip2.errors.AddressNotFoundError:
        return "Unknown"

def main():
    log_file_path = '/var/log/nginx/nginx-abf.access.log'
    output_json_path = '/tmp/botnet.json'
    output_ip_path = '/tmp/botnet.ip'
    # https://github.com/P3TERX/GeoLite.mmdb/releases/download/2025.01.22/GeoLite2-Country.mmdb 
    geoip_db_path = '/root/GeoLite2-Country.mmdb'

    # extract uniq ips
    unique_ips = extract_unique_ips(log_file_path)

    # remove local networks
    filtered_ips = [ip for ip in unique_ips if not is_private_ip(ip)]

    with open(output_ip_path, 'w') as ip_file:
        for ip in filtered_ips:
            ip_file.write(f"{ip}\n")

    print(f"Uniq ip saved to {output_ip_path}")
    print(f"Checking ip with GeoLite2...")

    # check country codes
    reader = geoip2.database.Reader(geoip_db_path)
    botnet_data = []
    total_ips = len(filtered_ips)
    for index, ip in enumerate(filtered_ips, start=1):
        print(f"Checking IP {ip} ({index} of {total_ips})")
        country = get_country_by_ip(ip, reader)
        botnet_data.append({
            'ip': ip,
            'country': country
        })

    reader.close()
    with open(output_json_path, 'w') as json_file:
        json.dump(botnet_data, json_file, indent=4)

    print(f"log saved: {output_json_path}")

if __name__ == '__main__':
    main()
