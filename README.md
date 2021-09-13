## Simple CLI for download graphs by hostname from Zabbix

#### Basic usage:
###### 1. Put your api_url, user, password in file ```.zabbix_graph_loader.yml``` like so:
```
api_url: 'https://zabbix.server.com'
user: 'test_user'
password: 'test_password'
```
###### 2. Run
```./zabbix_graph_loader.py --host test.com --only_summary``` - will load all graphs for host test.com with data for the last 24 hours and put it in one summary.png file.


```
usage: zabbix_graph_loader.py [-h] [--config CONFIG] [--host HOST] [--start START] [--end END] [--save SAVE] [--only_summary] [--list_graphs]
                              [--graphs GRAPHS]

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -f CONFIG
                        path to config file (default is ".zabbix_graph_loader.yml")
  --host HOST           hostname
  --start START, -s START
                        start time in format '2021-09-12 10:00:00'
  --end END, -e END     end time in format '2021-09-13 10:00:00'
  --save SAVE           path to save files (default is './{host}-{time}/'
  --only_summary        don't save each image, only summary
  --list_graphs         show available graphs names
  --graphs GRAPHS, -g GRAPHS
                        Graph name (ex. 'CPU Load Average'). Can be used several times
```                        
All optional arguments can be specified via the configuration file.
