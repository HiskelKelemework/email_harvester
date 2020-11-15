from bs4 import BeautifulSoup
from queue import Queue
import requests
import threading
import argparse
import time
import re


def harvester(url_queue, email_queue, visited_dict, domain=None):
    if not domain:
        regex = '[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}'
    else:
        regex = f'[a-z0-9]+[\._]?[a-z0-9]+[@]{domain}'

    while True:
        url = url_queue.get()
        visited_dict[url] = True
        print('checking in ' + url, end='\r')
        try:
            html = requests.get(url).content
        except:
            continue

        soup = BeautifulSoup(html, features='html.parser')

        all_text = soup.findAll(text=True)
        all_text = map(
            lambda each: each.lower(),
            filter(lambda each: each.strip(), all_text))

        all_text = ' '.join(all_text)

        for link in soup.find_all('a'):
            href = link.get('href')
            if href and not visited_dict.get(href):
                url_queue.put(link['href'])

        emails = re.findall(regex, all_text.lower())
        if (emails):
            for email in emails:
                email_queue.put(email)


def email_writer(email_queue):
    filename = str(time.time_ns()) + '.csv'
    with open(filename, 'w') as fd:
        while True:
            email = email_queue.get()
            if email == 'QUIT':
                break
            fd.write(email + '\n')
            print(email, end='\n')


def run_harvester(entry, domain=None):
    url_queue = Queue(maxsize=100)
    email_queue = Queue(maxsize=100)
    visited_dict = dict()
    url_queue.put(entry)

    harvester_args = (url_queue,
                      email_queue,
                      visited_dict,
                      domain)

    threads = [
        threading.Thread(target=harvester, args=harvester_args, daemon=True),
        threading.Thread(target=harvester, args=harvester_args, daemon=True),
        threading.Thread(target=harvester, args=harvester_args, daemon=True),
        threading.Thread(target=email_writer, args=(email_queue,), daemon=True)
    ]

    for thread in threads:
        thread.start()

    input()
    email_queue.put('QUIT')
    time.sleep(1)
    exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Email harvester tool')
    parser.add_argument('-d', type=str, help='ex: gmail.com')
    parser.add_argument('-e', type=str, help='entry point url', required=True)
    args = parser.parse_args()

    run_harvester(args.e, args.d)
