import json
import ipaddress

def ip_to_subnet(ip):
    network = ipaddress.IPv4Network(f"{ip}/24", strict=False)
    return str(network)

def main():
    input_json_path = '/tmp/botnet.json'

    with open(input_json_path, 'r') as json_file:
        botnet_data = json.load(json_file)

    subnets = set()
    for entry in botnet_data:
        ip = entry.get("ip")
        if ip:
            subnet = ip_to_subnet(ip)
            subnets.add(subnet)

    output_script_path = './block_subnets.sh'
    with open(output_script_path, 'w') as script_file:
        script_file.write("#!/bin/bash\n\n")

        script_file.write("# remove old iptables\n")
        script_file.write("iptables -D INPUT -m set --match-set blocked_subnets src -j DROP 2>/dev/null || true\n\n")

        script_file.write("# remove old ipse\n")
        script_file.write("ipset destroy blocked_subnets 2>/dev/null || true\n\n")

        script_file.write("# create new one ipset\n")
        script_file.write("ipset create blocked_subnets hash:net\n\n")

        script_file.write("# add subnets to ipset\n")
        for subnet in subnets:
            script_file.write(f"ipset add blocked_subnets {subnet}\n")

        script_file.write("\n# drop all traffic for botnet\n")
        script_file.write("iptables -I INPUT -m set --match-set blocked_subnets src -j DROP\n")

    import os
    os.chmod(output_script_path, 0o755)
    print(f"script to block subnets: {output_script_path}")
    print(f"BLOCKED {len(subnets)} subnets.")

if __name__ == '__main__':
    main()
