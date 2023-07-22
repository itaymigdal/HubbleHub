import re
import json
import base64
import logging
import colorama
import argparse
import requests
from collections import defaultdict

# API stuff
with open("GithubToken.txt", "rt") as f:
    access_token = f.read()
headers = {
    'Authorization': f'token {access_token}',
    'User-Agent': 'HubbleHub'
    }
api_url_starred = 'https://api.github.com/user/starred'
api_url_readme = "https://api.github.com/repos/{}/readme"

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

# Global vars
args = None
rate_limit_limit = None
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
    operators = re.findall(r'(\||&)', args.query)

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
            if operator == "|":
                result = result or (re.search(keyword_regex, description, re.IGNORECASE) is not None)
            elif operator == "&":
                result = result and (re.search(keyword_regex, description, re.IGNORECASE) is not None)

    return result


def get_readme_content(full_repo_name):
    global rate_limit_limit, rate_limit_remaining
    
    # Make the API request to get the README content
    api_url = api_url_readme.format(f"{full_repo_name}")
    response = requests.get(api_url, headers=headers)
    # Update limit rates
    rate_limit_limit = response.headers.get('X-RateLimit-Limit')
    rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
    if response.status_code == 200:
        # The response contains the content encoded in base64, so decode it
        readme_content_base64 = response.json()["content"]
        readme_content = base64.b64decode(readme_content_base64).decode("utf-8")
        return readme_content
    else:
        logger.warning(f"Failed to retrieve README content for {full_repo_name} (Status code {response.status_code}).")
        print(response.content)
        return ""


def print_rate_limit():
    logger.info(f"rate_limit_limit: {rate_limit_limit}")
    logger.info(f"rate_limit_remaining: {rate_limit_remaining}")


def complete():
    if args.rl:  # Print rate limit information
        print_rate_limit()
    if args.dr:  # Dump full repos dict
        with open("starred_repos.json", "wt") as f:
                json.dump(repos, f)


if __name__ == '__main__':

    # We want the response global so on KeyboardInterrupt we'll get an updated rate limit
    parser = argparse.ArgumentParser(description="Explore and filter your starred repositories")
    parser.add_argument("query", help="keywords query. e.g. \"('cobalt strike' | 'meterpreter') & 'red team'\"")
    parser.add_argument("-pl", help="include only those languages (split with '|')", default="*")
    parser.add_argument("-ms", type=int, help="minimum stars", default=0)
    parser.add_argument("-ir", action="store_true", help="ignore readme's (search only in repositories name and description)")
    parser.add_argument("-rl", action="store_true", help="print total and remaining rate limit")
    parser.add_argument("-dr", action="store_true", help="dump all starred repositories to json (regardless the query)")
    args = parser.parse_args()

    keywords, operators = parse_query()

    try:
        # Make the API request
        response = requests.get(api_url_starred, headers=headers)
        
        if args.rl:  # Extract and print rate limit information
            rate_limit_limit = response.headers.get('X-RateLimit-Limit')
            rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
            print_rate_limit()

        if response.status_code != 200:
            logger.error(f"Failed to retrieve starred repositories. Status code: {response.status_code}")
            quit()

        for repo in response.json():
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
        
