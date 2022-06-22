from Parsescript import prepare_readable_script

if __name__ == '__main__':
    data_s = '76a91461cf5af7bb84348df3fd695672e53c7d5b3f3db988ac'
    print('pushdata: ', data_s)
    script_b = bytes.fromhex(data_s)
    print('Decoded Script: ', prepare_readable_script(script_b))
    print('====================================================')
    data_s = '6a4c500029282c0002c5164b82ab2b42044dbe2b8573c969cc10d9e0bd03646ccf1e7497c4bf69678a7b6a99ce4f8dda595a2ed353f27c6195bdfd0528ff229f2619002759d5b9d236d1458d1ad7e7640b5948'
    print('PUSHDATA1: ', data_s)
    script_b = bytes.fromhex(data_s)
    print('Decoded Script: ', prepare_readable_script(script_b))
    print('====================================================')
    data_s = '47304402201f46c0a476592d44192773fb0ac385d5ab0fc286882016b220e055314989d70f0220151e45313207ef60d7e91b66f03bbaade27ad0fb0a78ca692ccdb4fa36202a66014d33014d0701434e54525052545903000800157934c4b76dd4598533af398d4600bc62c30e20001de8e1db9ab1622fb8b35eae514f6a2b848dec9000489ad6851b31a59f042593c28f49976ffe17abc6005d3d7d62a84e90b0cfcb455c4f73bc795115a5f2005eac6a674669c6c0de63177ae4b3f8f21579a5e90068430e5056f9b75beb0dbf415a8aa2c65305a89e00687fd8a1bcc5a7f48c540591a4e3521fe7a5d67300a393004b7d01b3ad81276898afb8203c1b631b8a40000085ecef53f53d0000000000000001808000000000000000300c0000000000000006030000000000000000c01000000000000000180e00000000000000030080000000000000006000000000000000000c00752103cff10054cf9cf2dbda64adb01ccfc46c3dee8fcf4a9ba7eb14015ebe97cc31f3ad0075740087'
    print('PUSHDATA2: ', data_s)
    script_b = bytes.fromhex(data_s)
    print('Decoded Script: ', prepare_readable_script(script_b))
