import dns.name
import dns.message
import dns.query
import dns.flags
import ipaddress

def getNodeAddresses(dnsseed: str): 
    dest = '8.8.8.8' 
    rdclass = 65535 
    domain = dns.name.from_text(dnsseed) 
    if not domain.is_absolute(): 
        domain = domain.concatenate(dns.name.root) 
    request = dns.message.make_query(domain, dns.rdatatype.A,  
                                    dns.rdataclass.IN)
    request.flags |= dns.flags.RD|dns.flags.RA|dns.flags.AD 
    request.find_rrset(request.additional, dns.name.root, rdclass, 
                       dns.rdatatype.OPT, create=True, 
                       force_unique=True) 
    responseudp = dns.query.udp(request, dest) 
    rrset = responseudp.answer 
    rrset_l = [] 
    for rrset_val in rrset: 
        rrset_l.extend(str(rrset_val).split("\n")) 
    ipaddr_l = [] 
    for rrset_s in rrset_l: 
        ipaddr_l.append(rrset_s.split(" ")[4]) 
    return ipaddr_l 

def getTestnetPeers(): 
    port = 18333 
    dns_seeds = [ 
            "testnet-seed.bitcoin.jonasschnelli.ch", 
            "seed.tbtc.petertodd.org", 
            "seed.testnet.bitcoin.sprovoost.nl", 
            "testnet-seed.bluematt.me" 
    ] 
    ipaddr_l = [] 
    for seed in dns_seeds: 
        ipaddr_l.extend(getNodeAddresses(seed)) 
    peers = [] 
    for ipaddr in ipaddr_l: 
        peers.append((ipaddr, port)) 
    return peers 
