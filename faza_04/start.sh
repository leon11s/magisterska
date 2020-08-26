#!/bin/sh

# set iptables
iptables -P OUTPUT DROP
iptables --append OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -p udp -d  8.8.8.8 -j ACCEPT
iptables -A OUTPUT -p tcp -d  8.8.8.8 -j ACCEPT

# edit /etc/resolv.conf DNS to 8.8.8.8
echo 'bmFtZXNlcnZlciA4LjguOC44Cm9wdGlvbnMgbmRvdHM6MA==' | base64 --decode > /etc/resolv.conf

# step 1: rename wget to wget2, curl to curl2
mv /usr/bin/wget /usr/bin/wget2
mv /usr/bin/curl /usr/bin/curl2

# create wget
echo 'IyEvdXNyL2Jpbi9weXRob24zCgppbXBvcnQgc3lzLCBzb2NrZXQsIHRpbWUsIHN1YnByb2Nlc3MKCmZyb20gdXJsbGliLnBhcnNlIGltcG9ydCB1cmxwYXJzZQoKIAoKdXJsc3RyaW5nPXN5cy5hcmd2WzFdCgppZiAiOi8vIiBub3QgaW4gdXJsc3RyaW5nOgoKICAgIHVybHN0cmluZyA9ICJodHRwOi8vIiArIHVybHN0cmluZwoKIAoKaG9zdCA9IHVybHBhcnNlKHVybHN0cmluZywgc2NoZW1lPScnLCBhbGxvd19mcmFnbWVudHM9VHJ1ZSkuaG9zdG5hbWUKCiAKCnRyeToKCiAgICBpcCA9IHNvY2tldC5nZXRob3N0YnluYW1lKGhvc3QpCgpleGNlcHQgRXhjZXB0aW9uOgoKICAgIHN5cy5leGl0KDApCgogCgpzdWJwcm9jZXNzLlBvcGVuKFsidG91Y2giLCAnL3RtcC9pcF8nICsgc3RyKGlwKV0pCgp0aW1lLnNsZWVwKDEpCgogCgpzeXMuYXJndlswXSA9ICIvdXNyL2Jpbi93Z2V0MiIKCnN1YnByb2Nlc3MuY2FsbChbKnN5cy5hcmd2XSk=' | base64 --decode > /usr/bin/wget
chmod +x /usr/bin/wget

# create curl
echo 'IyEvdXNyL2Jpbi9weXRob24zCgppbXBvcnQgc3lzLCBzb2NrZXQsIHRpbWUsIHN1YnByb2Nlc3MKCmZyb20gdXJsbGliLnBhcnNlIGltcG9ydCB1cmxwYXJzZQoKIAoKdXJsc3RyaW5nPXN5cy5hcmd2WzFdCgppZiAiOi8vIiBub3QgaW4gdXJsc3RyaW5nOgoKICAgIHVybHN0cmluZyA9ICJodHRwOi8vIiArIHVybHN0cmluZwoKIAoKaG9zdCA9IHVybHBhcnNlKHVybHN0cmluZywgc2NoZW1lPScnLCBhbGxvd19mcmFnbWVudHM9VHJ1ZSkuaG9zdG5hbWUKCiNwcmludCgiSG9zdDogIiArIGhvc3QpCgogCgp0cnk6CgogICAgaXAgPSBzb2NrZXQuZ2V0aG9zdGJ5bmFtZShob3N0KQoKZXhjZXB0IEV4Y2VwdGlvbjoKCiAgICBzeXMuZXhpdCgwKQoKIAoKc3VicHJvY2Vzcy5Qb3BlbihbInRvdWNoIiwgJy90bXAvaXBfJyArIHN0cihpcCldKQoKdGltZS5zbGVlcCgxKQoKIAoKc3lzLmFyZ3ZbMF0gPSAiL3Vzci9iaW4vY3VybDIiCgpzdWJwcm9jZXNzLmNhbGwoWypzeXMuYXJndl0p' | base64 --decode > /usr/bin/curl
chmod +x /usr/bin/curl

# run this perl script: fw.pl as root
echo 'IyEvdXNyL2Jpbi9wZXJsCgp3aGlsZSh0cnVlKXsKICAgIEBmaWxlcyA9IGdsb2IoJy90bXAvJyAuICdpcF8qJyApOwogICAgZm9yZWFjaCAoIEBmaWxlcyApIHsKICAgICAgICBteSgkcHJlZml4LCAkaXApID0gc3BsaXQoL18vLCAkXyApOwogICAgICAgIHN5c3RlbSgiaXB0YWJsZXMgLUEgT1VUUFVUIC1wIHRjcCAtZCAgJGlwIC1qIEFDQ0VQVCIpOwogICAgICAgIHVubGluaygkXyk7CiAgICB9CiAgICAgc3lzdGVtICJzbGVlcCAwLjEiOwp9' | base64 --decode > /root/fw.pl
chmod +x /root/fw.pl
perl /root/fw.pl &

#start ssh
/usr/sbin/sshd -D



