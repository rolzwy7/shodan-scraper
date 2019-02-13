import time
import csv
import argparse
from getpass import getpass

from shodan_scraper.session import ShodanSession, parse_search_query

parser = argparse.ArgumentParser(description="Shodan.io scraper")
parser.add_argument("query", help="Shodan Query (with no filters)")
parser.add_argument("--user", help="Shodan username")
parser.add_argument("--pwd", help="Shodan password")
parser.add_argument("--delay",
                    help="Delay between requests in seconds", type=int)
args = parser.parse_args()

delay = args.delay if args.delay else 2.5
unix_timestamp = int(time.time())

# User & Pwd
if args.user and args.pwd:
    if args.user:
        session_user = args.user
    if args.pwd:
        session_pwd = args.pwd
else:
    session_user = input("Username: ")
    session_pwd = getpass(prompt="Password: ")

# load ccodes
with open('ccodes.csv') as source:
    csv_reader = csv.reader(source, delimiter=',')
    next(csv_reader)
    countries = [row[1] for row in csv_reader]
    source.close()

# load country names
with open('ccodes.csv') as source:
    csv_reader = csv.reader(source, delimiter=',')
    next(csv_reader)
    countries_names = [row[0] for row in csv_reader]
    source.close()

# make queries
queries = [args.query]
all_queries = [
    {
        "query": '%s country:"%s"' % (query, country),
        "code": country,
        "name": countries_names[it]
    } for it, country in enumerate(countries) for query in queries
]

# print config
print("Delay         :", delay, "s")
print("Queries total :", len(all_queries))

# scrape
session = ShodanSession(session_user, session_pwd)
fh_results = open("results_(%s)_%s.txt" % (args.query, unix_timestamp), "wb")
fh_results.write(b"ccode, ipport\n")
for _ in all_queries:
    curr_code = _["code"]
    del _["code"]
    curr_name = _["name"]
    del _["name"]
    for page in [1, 2]:
        time.sleep(delay)
        try:
            response = session.scrape(_, page=page)
        except Exception as e:
            print("[!] Exception:", e)
            delay += .5
            print("[*] Delay increased to %ss" % delay)
            print("[*] Sleeping 10s")
            time.sleep(10.)
            print("[*] Creating new session")
            del session
            session = ShodanSession(session_user, session_pwd)

        results = parse_search_query(response)
        if results == []:
            break  # if theres no results on page 1
        for x in results:
            fh_results.write(("%s, %s\n" % (curr_code, x)).encode("utf8"))
            print(curr_name, x)
fh_results.close()
