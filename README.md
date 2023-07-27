
# HubbleHub

*Explore and filter your GitHub starred repositories*

![](/HubbleHub.PNG)

Ever felt like there are too many interesting and useful GitHub projects created each day and you just couldn't keep pace with them or remember all of them? 
Have you ever needed a tool but discovered that it existed only after it was no longer relevant?
Want to explore and filter the repositories you've already starred?
HubbleHub has got your back!

This tool accepts a query of keywords you're interested in, and searches across your starred repositories (name, description and readme), with the ability to filter languages, stars count, and more.

## Installation
1. `git clone https://github.com/itaymigdal/HubbleHub`
2. `cd HubbleHub`
3. `pip install -r requirements.txt`
4. Generate Github access token: `Settings -> Developer settings -> Personal access tokens -> Token (classic) -> Generate new token -> choose a name and enable only 'read:user' -> Generate token`
5. `echo <github_token> > GithubToken.txt`


## Usage

```
usage: HubbleHub.py [-h] [-pl PL] [-ms MS] [-ir] [-rl] [-dr] query

Explore and filter your GitHub starred repositories

positional arguments:
  query       keywords query

optional arguments:
  -h, --help  show this help message and exit
  -pl PL      include only those languages (split with '|')
  -ms MS      minimum stars
  -ir         ignore readme's (search only in repositories name and description)
  -rl         print total and remaining rate limit
  -bv         be verbose
  -dr         dump all starred repositories to json (regardless the query)

Query examples:
.\HubbleHub.py "'animal or ('dog' and 'cat' and 'bird')'"
.\HubbleHub.py "('cobalt strike' or 'meterpreter') and 'red team'"
```

Ensure that when passing the query, it is enclosed within double quotes and each keyword is also wrapped with quotes. This is necessary due to query parsing.