Simple CLI for download graph by hostname from Zabbix

./zabbix_graph_loader.py --host test.com --start "2021-09-10 21:40:02" --end "2021-09-10 23:40:02" --only_summary -g "CPU Load Average" -g "Memory Utilization" -g "Iowait" -g "MySQL Slow Queries" -g "Apache: Scoreboard"

usage: zabbix_graph_loader.py [-h] [--config CONFIG] [--host HOST] [--start START] [--end END] [--save SAVE] [--only_summary] [--list_graphs]
                              [--graphs GRAPHS]

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -f CONFIG
                        path to config file (default is ".zabbix_graph_loader.yml")
  --host HOST           hostname
  --start START, -s START
                        start time in format '2021-09-12 17:57:44'
  --end END, -e END     end time in format '2021-09-13 17:57:44'
  --save SAVE           path to save files (default is './{host}-{time}/'
  --only_summary        don't save each image, only summary
  --list_graphs         show available graphs names
  --graphs GRAPHS, -g GRAPHS
                        Graph name (ex. 'CPU Load Average'). Can be used several times