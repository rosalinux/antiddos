
prepare geoip data

```
wget https://github.com/P3TERX/GeoLite.mmdb/releases/download/2025.01.22/GeoLite2-Country.mmdb
```

```
pip3 install geoip2
```

```
python ddos2.py
```

```
python prep_banlist.py
```

```
sh block_subnets.sh
```
