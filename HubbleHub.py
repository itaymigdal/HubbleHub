import requests


with open("GithubToken.txt", "rt") as f:
    access_token = f.read()
headers = {'Authorization': f'token {access_token}'}

# Make the API request
response = requests.get('https://api.github.com/user/starred', headers=headers)

if response.status_code == 200:
    starred_repos = response.json()
    for repo in starred_repos:
        print(repo)
        quit()
else:
    print(f"Failed to retrieve starred repositories. Status code: {response.status_code}")
