#!/usr/bin/env python3

from pyzabbix import ZabbixAPI, ZabbixAPIException
from PIL import Image
import requests
import sys
import os
from io import BytesIO
import datetime
import argparse
import yaml
import traceback

TIMEZONE_OFFSET = 3.0  # Moscow Time (UTC+03:00)
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class Config:
    def __init__(self, conf_path):
        self.api_url = None
        self.user = None
        self.password = None
        self.host = None
        self.stat_start = None
        self.stat_end = None
        self.save_path = None
        self.only_summary = None
        self.graphs = None
        self.parse(conf_path)

    def parse(self, path):
        with open(path, 'r') as stream:
            conf = yaml.safe_load(stream)
            if 'api_url' in conf:
                self.api_url = conf['api_url']
            if 'user' in conf:
                self.user = conf['user']
            if 'host' in conf:
                self.host = conf['host']
            if 'password' in conf:
                self.password = conf['password']
            if 'only_summary' in conf:
                self.only_summary = conf['only_summary']
            if 'graphs' in conf:
                self.graphs = conf['graphs']
            if 'save_path' in conf:
                self.save_path = conf['save_path']
            if 'stat_start' in conf:
                self.stat_start = conf['stat_start']
            if 'stat_end' in conf:
                self.stat_end = conf['stat_end']


def get_png(graph_id, graph_name):
    file_name = graph_name.lower().replace(' ', '_').replace('/', '-')
    print('"{gname}" saving to {path}/{fname}.png'.format(gname=graph_name, path=params.save_path, fname=file_name))
    login_data = {'autologin': '1', 'name': params.user, 'password': params.password, 'enter': 'Sign in'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0',
               'Content-type': 'application/x-www-form-urlencoded'}
    session = requests.session()
    login = session.post(params.api_url + "/index.php", params=login_data, headers=headers)

    try:
        if login.cookies['zbx_sessionid']:
            graph_url = '''{url}/chart2.php?profileIdx=web.graphs.filter&graphid={id}&from={f}&to={t}'''.format(
                url=params.api_url,
                id=graph_id,
                f=params.stat_start.strftime(TIME_FORMAT),
                t=params.stat_end.strftime(TIME_FORMAT))
            graph_req = session.get(graph_url)
            graph_png = Image.open(BytesIO(graph_req.content))
            if not params.only_summary:
                graph_png.save('{path}/{name}.png'.format(path=params.save_path, name=file_name))
            merge_png(summary_file, graph_png)
    except Exception:
        print(traceback.format_exc())
        sys.exit("Error: Could not log in to retrieve graph")


def merge_png(sum_file, image):
    if not os.path.isfile(sum_file):
        image.save(sum_file)
        return
    else:
        max_height, max_width, cur_height = 0, 0, 0
        with Image.open(sum_file) as sum:
            max_height = sum.height + image.height
            if image.width > sum.width:
                max_width = image.width
            else:
                max_width = sum.width
            cur_height = sum.height

            dst = Image.new('RGB', (max_width, max_height))
            dst.paste(sum, (0, 0))
            dst.paste(image, (0, cur_height))
            dst.save(sum_file)


def main():
    if not os.path.isdir(params.save_path):
        os.makedirs(params.save_path)
    if os.path.isfile(summary_file):
        os.remove(summary_file)

    # zapi.login(api_token='xxxxx')
    print('Connected to Zabbix API Version %s' % zapi.api_version())
    print('TimeFrame: {} <--> {}'.format(params.stat_start.strftime(TIME_FORMAT), params.stat_end.strftime(TIME_FORMAT)))

    for h in zapi.host.get(output="extend", filter={'host': params.host}):
        host_id = h['hostid']
        for g in zapi.graph.get(output="extend", hostids=host_id):
            if args.list_graphs:
                print(g['name'])
            else:
                if params.graphs is not None and g['name'] in params.graphs:
                    get_png(g['graphid'], g['name'])


if __name__ == '__main__':
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=TIMEZONE_OFFSET)
    now_minus_24 = now - datetime.timedelta(hours=24)
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-f', type=str, help='path to config file (default is ".zabbix_graph_loader.yml")',
                        default='.zabbix_graph_loader.yml')

    parser.add_argument('--host', help="hostname", type=str)
    parser.add_argument('--start', '-s', type=str,
                        help="start time in format '{}'".format(now_minus_24.strftime(TIME_FORMAT)))
    parser.add_argument('--end', '-e', type=str, help="end time in format '{}'".format(now.strftime(TIME_FORMAT)))
    parser.add_argument('--save', type=str, help="path to save files (default is './{host}-{time}/'")
    parser.add_argument('--only_summary', help="don't save each image, only summary", action="store_true",
                        default=False)
    parser.add_argument('--list_graphs', help="show available graphs names", action="store_true",
                        default=False)
    parser.add_argument('--graphs', '-g', type=str,
                        help="Graph name (ex. 'CPU Load Average'). Can be used several times",
                        action='append')
    args = parser.parse_args()
    params = Config(args.config)

    if args.host:
        params.host = args.host
    if params.host is None:
        parser.print_help(sys.stderr)
        quit(0)

    if args.start:
        try:
            params.stat_start = datetime.datetime.strptime(args.start, TIME_FORMAT)
        except ValueError:
            print('ERROR: Bad time format')
            parser.print_help(sys.stderr)
            quit(0)
    else:
        params.stat_start = now - datetime.timedelta(hours=24)
    if args.end:
        try:
            params.stat_end = datetime.datetime.strptime(args.end, TIME_FORMAT)
        except ValueError:
            print('ERROR: Bad time format')
            parser.print_help(sys.stderr)
            quit(0)
    else:
        params.stat_end = now

    if args.only_summary:
        params.only_summary = args.only_summary

    save_dir = '{h}_{s}-{e}'.format(h=params.host, s=params.stat_start.strftime('%Y-%m-%d_%H:%M'),
                                    e=params.stat_end.strftime('%Y-%m-%d_%H:%M'))
    if args.save:
        params.save_path = '{p}/{s}'.format(p=args.save.rstrip('/'), s=save_dir)
    else:
        params.save_path = './{s}'.format(s=save_dir)
    summary_file = '{path}/summary.png'.format(path=params.save_path)

    if args.graphs:
        params.graphs = args.graphs
    try:
        zapi = ZabbixAPI(params.api_url)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as er:
        print(er)
        quit(0)
    try:
        zapi.login(params.user, params.password)
    except ZabbixAPIException as er:
        print(er)
        quit(0)

    try:
        main()
    except KeyboardInterrupt:
        print('Aborted')
