#!/usr/bin/python3

from re import search
from requests import get
from termcolor import colored
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from jsbeautifier import beautify
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor

from lib.Functions import starter, manage_output
from lib.PathFunctions import PathFunction
from lib.Globals import *

parser = ArgumentParser(description=colored('Javascript Scanner', color='yellow'), epilog=colored("Enjoy bug hunting", color='yellow'))
input_group = parser.add_mutually_exclusive_group()
output_group = parser.add_mutually_exclusive_group()
input_group.add_argument('---', '---', action="store_true", dest="stdin", help="Stdin")
input_group.add_argument('-w', '--wordlist', type=str, help='Absolute path of wordlist')
parser.add_argument('-d', '--domain', type=str, help="Domain name")
output_group.add_argument('-oD', '--output-directory', type=str, help="Output directory")
output_group.add_argument('-o', '--output', type=str, help="Output file")
parser.add_argument('-t', '--threads', type=int, help="Number of threads")
parser.add_argument('-b', '--banner', action="store_true", help="Print banner and exit")
argv = parser.parse_args()
input_wordlist = starter(argv)

def scan_js(url: str) -> bool:
    FPathApp = PathFunction()
    output_list = []
    urlparser = urlparse(url)
    if search(".*\.js$", urlparser.path):
        try:
            jsurl = FPathApp.slasher(FPathApp.urler(urlparser.netloc)) + FPathApp.payloader(urlparser.path)
            print(f"{ColorObj.information} Trying to get data from {colored(jsurl, color='cyan')}")
            output_list.append(manage_output(f"{jsurl}  <--- URL\n"))
            jsreq = get(jsurl)
            jstext = str(beautify(jsreq.text)).split('\n')
            for jsline in jstext:
                for dom_source in dom_sources_regex:
                    if search(dom_source, jsline):
                        print(f"{ColorObj.good} Found sensitive data: {colored(jsline, color='cyan')}")
                        output_list.append(manage_output(f"{jsline.strip(' ')} <--- From regex {dom_source}\n"))
                for dom_sink in dom_sinks_regex:
                    if search(dom_sink, jsline):
                        print(f"{ColorObj.good} Found sensitive data: {colored(jsline, color='cyan')}")
                        output_list.append(manage_output(f"{jsline.strip(' ')} <--- From regex {dom_sink}\n"))
            return True
        except Exception as E:
            print(f"{ColorObj.bad} Exception {E},{E.__class__} occured")
            return False
    if not search(".*\.js$", urlparser.path):
        try:
            jsurl = FPathApp.slasher(FPathApp.urler(urlparser.netloc)) + FPathApp.payloader(urlparser.path)
            print(f"{ColorObj.information} Trying to get data from {colored(jsurl, color='cyan')}")
            output_file.write(manage_output(f"{jsurl} <--- URL\n"))
            jsreq = get(jsurl)
            jsx = BeautifulSoup(jsreq.text, 'html.parser')
            jssoup = jsx.find_all("script")
            for jscript in jssoup:
                if jscript != None:
                    jstext = str(beautify(jscript.string)).split('\n')
                    for jsline in jstext:
                        for dom_source in dom_sources_regex:
                            if search(dom_source, jsline):
                                print(f"{ColorObj.good} Found sensitive data: {colored(jsline, color='cyan')}")
                                output_list.append(manage_output(f"{jsline} <--- From regex {dom_source}\n"))
                        for dom_sink in dom_sinks_regex:
                            if search(dom_sink, jsline):
                                print(f"{ColorObj.good} Found sensitive data: {colored(jsline, color='cyan')}")
                                output_list.append(manage_output(f"{jsline} <--- From regex {dom_sink}\n"))
            return True
        except Exception as E:
            print(f"{ColorObj.bad} Exception {E},{E.__class__} occured")
            return False
try:
    def main():
        global input_wordlist
        with ThreadPoolExecutor(max_workers=argv.threads) as submitter:
            submitter.submit(scan_js, input_wordlist)

    if __name__ == "__main__":
        main()
except Exception as E:
    print(E,E.__class__)
