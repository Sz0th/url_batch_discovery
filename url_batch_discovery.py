import os
import sys
import time
import json
import argparse
import threading
import pandas as pd


def print_wait():
    animation = "|/-\\"
    idx = 0
    while (num == 0):
        print('\033[1;33m[+] 正在获取数据中 \033[0m' + animation[idx % len(animation)], end="\r")
        idx += 1
        time.sleep(0.1)


def main(file, match_string, output_path, ports, threads):
    print('''\033[1;33m[+] 扫描线程：%s
[+] 导出目录：%s
[+] 待扫描文件：%s
[+] 待扫描端口：%s
[+] 待匹配字符串：%s
          \033[0m'''%(threads,output_path,file,ports,match_string))
    if file == './tmp/tmp.txt':
        with open(file) as f:
            file_url = f.readlines()[0]
    else:
        file_url = file
    global num
    num = 0
    t = threading.Thread(target=print_wait)
    t.start()
    time.sleep(3)
    if len(file_url.split('/')) > 2 and '//' not in file_url:
        file_title = output_path + file_url.split('/')[-1].split('.')[-2] + '_tmp.txt'
        file_path = output_path + file_url.split('/')[-1].split('.')[-2] + '.xlsx'
    else:
        file_title = output_path + file_url.replace('.', '_') + '_tmp.txt'
        file_path = output_path + file_url.replace('.', '_') + '.xlsx'
    pool = []
    if match_string == 'null':
        os.system(
            'httpx -l %s -threads %s -title -title -json -silent -ports %s -follow-redirects > %s' % (
                file, threads, ports, file_title))
    else:
        os.system(
            'httpx -l %s -threads %s -title -title -json -silent -ports %s -match-string "%s" -follow-redirects > %s' % (
                file, threads, ports, match_string, file_title))

    with open(file_title) as f:
        f = f.readlines()
        for i in f:
            i = json.loads(i.replace('\n', ''))
            info = {}
            info['url'] = i['url']
            info['title'] = i['title']
            info['webserver'] = i['webserver']
            info['status-code'] = i['status-code']
            info['ip'] = i['ip']
            info['content-length'] = i['content-length']
            info['response-time'] = i['response-time']
            pool.append(info)

    df = pd.DataFrame(pool)
    os.remove(file_title)
    num = 1
    if len(pool) == 0:
        print('\033[1;31m\n[-] 未获取到数据\033[0m')
    else:
        df.to_excel(file_path,
                    columns=['url', 'title', 'webserver', 'status-code', 'ip', 'content-length', 'response-time'],
                    index=False, encoding='utf_8_sig')
        print('\033[1;33m\n[+] 数据获取完毕，已导出到 %s \033[0m' % file_path)


if __name__ == '__main__':
    print('''\033[1;34m                                                                      
 _____ _____ __       _____     _       _      ____  _                             
|  |  | __  |  |     | __  |___| |_ ___| |_   |    \|_|___ ___ ___ _ _ ___ ___ _ _ 
|  |  |    -|  |__   | __ -| .'|  _|  _|   |  |  |  | |_ -|  _| . | | | -_|  _| | |
|_____|__|__|_____|  |_____|__,|_| |___|_|_|  |____/|_|___|___|___|\_/|___|_| |_  |
                                                                              |___|
 Version: 0.2               date: 2021.1.7
 公众号：TeamsSix           博客：teamssix.com
 Author: TeamsSix           GitHub：https://github.com/teamssix/url_batch_discovery
 注：本工具核心功能来自于优秀的 httpx 工具，使用本工具需要先安装 httpx，httpx 项目地址：https://github.com/projectdiscovery/httpx
\033[0m''')
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', dest='list', help='指定URL列表文件')
    parser.add_argument('-m', dest='match', help='指定要匹配的关键字，返回结果中将只包含存在该关键字的内容')
    parser.add_argument('-o', dest='output', help='导出的文件路径，默认保存在./output/文件夹内，导出文件格式为xlsx，格式：/path1/path2/')
    parser.add_argument('-p', dest='port', help='指定要检测的端口，默认80和443端口，格式：80,443,8000-8010')
    parser.add_argument('-t', dest='threads', help='指定线程大小，默认50个线程')
    parser.add_argument('-u', dest='url', help='指定单个URL')
    args = parser.parse_args()

    if not os.path.exists('./output'):
        os.makedirs('./output')

    if not args.list and not args.url:
        print('\033[1;31m[-] 未指定要访问的 URL 或者 URL 列表，帮助信息如下：\n\033[0m')
        parser.print_help()
        sys.exit()

    if args.match:
        match_string = args.match
    else:
        match_string = 'null'

    if args.output:
        output_path = args.output
        if not os.path.exists(args.output):
            print('\033[1;31m[-] 系统中未找到 %s 路径，请确认后再次执行。\n\033[0m' % output_path)
            sys.exit()
    else:
        output_path = './output/'

    if args.port:
        ports = args.port
    else:
        ports = '80,443'

    if args.threads:
        threads = args.threads
    else:
        threads = '100'
    if args.url:
        url = args.url
        if not os.path.exists('./tmp'):
            os.makedirs('./tmp')
        with open('./tmp/tmp.txt', 'w') as w:
            w.write(url)
        main('./tmp/tmp.txt', match_string, output_path, ports, threads)
        os.remove('./tmp/tmp.txt')
        os.removedirs('./tmp/')
    elif args.list:
        file = args.list
        if not os.path.isfile(file):
            print('\033[1;31m[-] 系统中未找到 %s 文件，请确认后再次执行。\n\033[0m' % file)
            sys.exit()
        else:
            with open(file) as f:
                f = f.readlines()
                if len(f) == 0:
                    print('\033[1;31m[-] %s 文件中貌似没有数据，请确认后再次执行。\n\033[0m' % file)
                    sys.exit()
                else:
                    main(file, match_string, output_path, ports, threads)
