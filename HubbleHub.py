import re
import json
import base64
import logging
import colorama
import argparse
import requests
from sys import argv
from collections import defaultdict

# Tool banner
banner = """
 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣆⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⠟⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠿⠿⣧⠀⠀

⠀⠀⠀⣼⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⢠⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠻⣿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣠⣿⣿⣧⣄⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣿⠿⠿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⡿⠛⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⠟⠋⠉⠛⠿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀

                                                        ⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                        ⠀⣼⡏⠀⢰⣿⣶⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                        ⢸⡟⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                        ⠈⠁⠀⢾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⢀⣄⣀⠀⠀⠀⠀⠀⠀⠀⢠⣦⣤⣀⡀⠀⠀⠀⠀⠀⠀
                                                        ⠀⠀⠀⠀⠈⠉⠙⠛⠿⢿⣿⣿⣿⣿⣿⡏⠀⣾⣿⣿⣿⣷⣶⣤⣄⣀⠀⠉⢻⠿⠿⣿⣷⣦⣤⠀⠀⠀
                                                        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠛⠟⠀⠸⠿⣿⣿⣿⣿⣿⣿⣿⡿⠁⣤⣯⣀⡀⠀⡸⠉⠁⠀⠀⠀
                                                        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢉⣍⡛⠿⠿⣿⠁⣸⣿⣿⣿⣿⣿⡷⠀⠀⠀⠀⠀
                                                        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠟⠃⠀⠀⠀⠀⠀⠉⠉⠛⠻⠿⠁⠀⠀⠀⠀⠀
                                                        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
  _    _       _     _     _      _    _       _        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
 | |  | |     | |   | |   | |    | |  | |     | |       ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠌⠀⠃⠀⢂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
 | |__| |_   _| |__ | |__ | | ___| |__| |_   _| |__     ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡘⠀⠀⠀⠀⠈⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
 |  __  | | | | '_ \| '_ \| |/ _ \  __  | | | | '_ \    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠀⠀⠀⠀⠀⠀⠘⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
 | |  | | |_| | |_) | |_) | |  __/ |  | | |_| | |_) |   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠁⠀⠀⠀⠀⠀⠀⠀⠰⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
 |_|  |_|\__,_|_.__/|_.__/|_|\___|_|  |_|\__,_|_.__/    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⢡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                                      ⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣀⣀⡀⢈⣀⣀⣀⣀⣀⠀⣀⣀⣀⣀⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
 https://github.com/itaymigdal/HubbleHub                ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢁⣾⣿⡿⠿⠿⠿⠸⠿⠿⠿⠿⠿⠧⠹⠿⠿⢿⣿⣿⣿⣶⣶⣶⣶
 By Itay Migdal                                         ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣤⣤⣤⣄⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣤⣤⣤⣤⣿⣿⣿⣿

"""

# Init colorama
colorama.init(autoreset=True)

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Create a custom formatter
log_formatter = logging.Formatter(f"{colorama.Fore.YELLOW}[%(levelname)s] {colorama.Style.RESET_ALL}%(message)s")
# Create a console handler and set the formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
# Add the console handler to the logger
logger.addHandler(console_handler)

# API stuff
try:
    with open("GithubToken.txt", "rt") as f:
        access_token = f.read()
except FileNotFoundError:
    logger.error("Missing GithubToken file")
    quit()
    
headers = {
    'Authorization': f'token {access_token}',
    'User-Agent': 'HubbleHub'
    }
api_url_starred = 'https://api.github.com/user/starred'
api_url_readme = "https://api.github.com/repos/{}/readme"

# Global vars
args = None
rate_limit_remaining = None
repos = defaultdict(dict)
repo_fields = [
    "name",
    "full_name",
    "html_url",
    "description",
    "topics",
    "language",
    "stargazers_count",
    "forks_count",
    "created_at",
    "updated_at"
]


def parse_query():
    # Use regular expressions to extract keywords and operators
    keywords = [match[1] for match in re.findall(r'(["\'])(.*?)\1', args.query)]
    operators = re.findall(r'(?:or|and)', args.query)

    return keywords, operators


def evaluate_query(description, keywords, operators):
    # Implement query evaluation using boolean logic
    result = True
    for i, keyword in enumerate(keywords):
        keyword_regex = fr'\b{re.escape(keyword)}s?\b'
        if i == 0:
            result = re.search(keyword_regex, description, re.IGNORECASE) is not None
        else:
            operator = operators[i - 1]
            if operator == "or":
                result = result or (re.search(keyword_regex, description, re.IGNORECASE) is not None)
            elif operator == "and":
                result = result and (re.search(keyword_regex, description, re.IGNORECASE) is not None)

    return result


def get_readme_content(full_repo_name):
    global rate_limit_remaining
    
    # Make the API request to get the README content
    api_url = api_url_readme.format(f"{full_repo_name}")
    response = requests.get(api_url, headers=headers)
    # Update remaining rate limit
    rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
    if args.rl:  # print rate limit information
        if int(rate_limit_remaining) % 10 == 0:
            logger.info(f"rate_limit_remaining: {rate_limit_remaining}")
    if response.status_code == 200:
        # The response contains the content encoded in base64, so decode it
        readme_content_base64 = response.json()["content"]
        readme_content = base64.b64decode(readme_content_base64).decode("utf-8")
        return readme_content
    else:
        if args.bv:
            logger.warning(f"Failed to retrieve README content for {full_repo_name} (Status code {response.status_code}).")
        return ""


def complete():
    if args.rl:  # Print rate limit information
        logger.info(f"rate_limit_remaining: {rate_limit_remaining}")
    if args.dr:  # Dump full repos dict
        with open("starred_repos.json", "wt") as f:
                json.dump(repos, f)


def get_all_starred_repos():
    global headers, rate_limit_remaining

    all_starred_repos = []
    page_number = 1

    while True:
        if args.bv:
            logger.info(f"Retrieving starred projects (page={page_number})")
        response = requests.get(api_url_starred, headers=headers, params={"page": page_number})
        if response.status_code != 200:
            logger.error(f"Failed to retrieve starred repositories on page {page_number}. Status code: {response.status_code}")
            return []

        rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
        if args.rl:  # print rate limit information
            if page_number == 1:
                logger.info(f"rate_limit_limit: {response.headers.get('X-RateLimit-Limit')}")
            if int(rate_limit_remaining) % 10 == 0:
                logger.info(f"rate_limit_remaining: {rate_limit_remaining}")
                   
        starred_repos = response.json()
        all_starred_repos.extend(starred_repos)

        # Check if there are more pages to retrieve
        link_header = response.headers.get('Link')
        if not link_header or 'rel="next"' not in link_header:
            break

        page_number += 1

    return all_starred_repos


if __name__ == '__main__':

    example_usage = f'''
Query examples:
{argv[0]} "'animal or ('dog' and 'cat' and 'bird')'"
{argv[0]} "('cobalt strike' or 'meterpreter') and 'red team'"
    '''

    parser = argparse.ArgumentParser(
    description="Explore and filter your GitHub starred repositories",
    epilog=example_usage,  
    formatter_class=argparse.RawDescriptionHelpFormatter,  # Preserve newlines in epilog
)
    parser.add_argument("query", help="keywords query")
    parser.add_argument("-pl", help="include only those languages (split with '|')", default="*")
    parser.add_argument("-ms", type=int, help="minimum stars", default=0)
    parser.add_argument("-ir", action="store_true", help="ignore readme's (search only in repositories name and description)")
    parser.add_argument("-rl", action="store_true", help="print total and remaining rate limit")
    parser.add_argument("-bv", action="store_true", help="be verbose")
    parser.add_argument("-dr", action="store_true", help="dump all starred repositories to json (regardless the query)")
    args = parser.parse_args()

    keywords, operators = parse_query()

    print(banner)

    try:
        # Make the API requests to retrieve all starred projects
        all_starred_repos = get_all_starred_repos()
        if args.bv:
            logger.info("Parsing results and fetching README's")
        for repo in all_starred_repos:
            if args.dr:  # Store results on a dictionary
                repos[repo["id"]] = {}
                # Fetch needed fields from the repo details
                for field in repo_fields:
                    repos[repo["id"]][field] = repo[field]
                # Get Also README
                repos[repo["id"]]["readme"] = get_readme_content(repo["full_name"]) 
                       
            if repo["stargazers_count"] >= args.ms: # Only if repo has the minimum stars
                if args.pl == "*" or repo["language"] in args.pl.split("|"):  # Only if repo from the included languages
                    try:
                        repo_content = f'{repo["name"].lower()} {repo["description"].lower()} '
                    except AttributeError:  # Missing description
                        repo_content = repo["name"].lower()
                    if not args.ir: # Include readme
                        repo_content += get_readme_content(repo["full_name"])
                    if evaluate_query(repo_content, keywords, operators):
                        print(
                            f'{colorama.Fore.RED}[RESULT] '
                            f'{colorama.Fore.CYAN}{repo["html_url"]}: '
                            f'{colorama.Fore.MAGENTA}{repo["description"]} '
                            f'{colorama.Fore.GREEN}({repo["stargazers_count"]}\u2605, {repo["language"]})'
                        )

        complete() 


    except KeyboardInterrupt:
        logger.error("Script interrupted")
        complete()
        
