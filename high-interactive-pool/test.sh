lscpu | grep Model
ls -lh $(which ls)
uname -a
cat /proc/cpuinfo | grep name | head -n 1 | awk '{print $4,$5,$6,$7,$8,$9;}'
free -m | grep Mem | awk '{print $2 ,$3, $4, $5, $6, $7}'
mkdir lalalala
touch hhi
chmod +x hhi
wget google.com
echo "Zsolt123\ndOYuxOqW3mMc\ndOYuxOqW3mMc\n"|passwd