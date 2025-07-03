from scapy.all import *
import random

def random_ipv4():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

def convert_ipv6_to_ipv4(pkt):
    if IPv6 in pkt:
        # Get L4 layer (e.g., TCP/UDP) and payload
        ip6 = pkt[IPv6]
        l4 = ip6.payload.copy()

        # Build new IPv4 layer
        ip4 = IP(
            src=random_ipv4(),
            dst=random_ipv4(),
            proto=ip6.nh  # next header in IPv6 becomes proto in IPv4
        )

        # Rebuild full packet
        if Ether in pkt:
            eth = pkt[Ether].copy()
            eth.remove_payload()  # remove all layers above Ether
            eth.type = 0x0800     # correct EtherType for IPv4
            new_pkt = eth / ip4 / l4
        else:
            new_pkt = ip4 / l4

        return new_pkt

    else:
        return pkt  # Leave non-IPv6 packets unchanged

def process_pcap(input_file, output_file):
    packets = rdpcap(input_file)
    converted = [convert_ipv6_to_ipv4(pkt) for pkt in packets]
    wrpcap(output_file, converted)
    print(f"[+] Written cleaned IPv4-only pcap to: {output_file}")

# Example usage:
# process_pcap("input.pcap", "output_ipv4_clean.pcap")


