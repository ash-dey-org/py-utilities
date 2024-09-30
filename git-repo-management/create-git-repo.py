# to do
# fix adding team permission to repo
# fix branch protection rule, who can push to branch

# pip install requests
# to fic ssl certificate error issue
# pip install pip-system-certs

import os
import requests
from requests.auth import HTTPBasicAuth
import json
import base64

# Replace these variables with your GitHub username and personal access token
USERNAME = os.environ["GITHUB_USER"]
TOKEN = os.environ["GITHUB_TOKEN"]

# Organization and repository details
organization = os.environ["GITHUB_ORG"]
dev_team = "dev-team"
ops_team = "ops-team"

# Helper function to make authenticated GitHub API requests
def github_request(method, url, data=None, headers=None):
    auth = HTTPBasicAuth(USERNAME, TOKEN)
    response = requests.request(method, url, auth=auth, data=json.dumps(data) if data else None, headers=headers)
    return response

# Function to create a GitHub repository
def create_repository(repo_name, default_branch='develop'):
    repo_url = f'https://api.github.com/orgs/{organization}/repos'
    repo_data = {
        'name': repo_name,
        'private': False,  # Set the repository as public
        'auto_init': True,  # Automatically initialize the repository with a README
        'default_branch': default_branch
    }

    response = github_request('POST', repo_url, data=repo_data)
    if response.status_code == 201:
        print(f'Repository {repo_name} created successfully!')
        return response.json()  # Return the repo information
    else:
        print(f'Failed to create repository: {response.json()}')
        exit(1)

# Function to create branches
def create_branches(repo_name, branches, default_branch_sha):
    for branch in branches:
        if branch == 'develop':
            continue

        # Create the branch by referencing the default branch
        create_branch_url = f'https://api.github.com/repos/{organization}/{repo_name}/git/refs'
        branch_data = {
            'ref': f'refs/heads/{branch}',
            'sha': default_branch_sha
        }

        response = github_request('POST', create_branch_url, data=branch_data)
        if response.status_code == 201:
            print(f'Branch {branch} created successfully!')
        else:
            print(f'Failed to create branch {branch}: {response.json()}')

# Function to upload a local .gitignore file to the develop branch
def upload_gitignore_to_develop(repo_name, file_path, branch='develop'):
    try:
        # Read the content of the local .gitignore file
        with open(file_path, 'r') as file:
            gitignore_content = file.read()

        # GitHub API URL for creating the .gitignore file in the repo
        file_url = f'https://api.github.com/repos/{organization}/{repo_name}/contents/.gitignore'

        # Get the SHA of the branch
        branch_sha_url = f'https://api.github.com/repos/{organization}/{repo_name}/git/ref/heads/{branch}'
        response = github_request('GET', branch_sha_url)
        if response.status_code == 200:
            branch_sha = response.json()['object']['sha']
        else:
            print(f'Failed to get SHA for branch {branch}: {response.json()}')
            exit(1)

        # Prepare data to upload the .gitignore file
        file_data = {
            "message": f"Add .gitignore file to {branch} branch",  # Commit message
            "content": base64.b64encode(gitignore_content.encode()).decode(),  # Base64 encoded content
            "branch": branch
        }

        response = github_request('PUT', file_url, data=file_data)
        if response.status_code == 201:
            print(f'.gitignore file uploaded to {branch} branch successfully!')
        else:
            print(f'Failed to upload .gitignore file to {branch}: {response.json()}')
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred while uploading the .gitignore file: {str(e)}")

# Function to merge develop branch into other branches
def merge_develop_into_branch(repo_name, target_branch, source_branch='develop'):
    print(f"Merging {source_branch} into {target_branch}...")
    merge_url = f'https://api.github.com/repos/{organization}/{repo_name}/merges'
    merge_data = {
        "base": target_branch,  # Target branch to merge into
        "head": source_branch,  # Source branch to merge from
        "commit_message": f"Merge {source_branch} into {target_branch}"
    }

    response = github_request('POST', merge_url, data=merge_data)
    if response.status_code == 201:
        print(f'Successfully merged {source_branch} into {target_branch}!')
    elif response.status_code == 204:
        print(f"No changes to merge from {source_branch} to {target_branch}.")
    else:
        print(f'Failed to merge {source_branch} into {target_branch}: {response.json()}')

# Function to create branch protection rule
def create_branch_protection(repo_name):
    protection_url = f'https://api.github.com/repos/{organization}/{repo_name}/branches/main/protection'
    protection_data = {
        "required_status_checks": None,
        "enforce_admins": None,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 1
        },
        "restrictions": None
    }

    headers = {'Accept': 'application/vnd.github.luke-cage-preview+json'}
    response = github_request('PUT', protection_url, data=protection_data, headers=headers)
    if response.status_code == 200:
        print('Branch protection rule created successfully!')
    else:
        print(f'Failed to create branch protection rule: {response.json()}')

def get_teams(organization):
    url = f'https://api.github.com/orgs/{organization}/teams'
    response = github_request('GET', url)
    if response.status_code == 200:
        teams = response.json()
        print("Teams in the organization:")
        for team in teams:
            print(f"Team name: {team['name']}, Slug: {team['slug']}")
        return teams
    else:
        print(f"Failed to fetch teams: {response.json()}")
        exit(1)

# Function to add teams to repository
def assign_team_permissions(repo_name, teams):
    for team, role in teams.items():
        team_url = f'https://api.github.com/orgs/{organization}/teams/{team}/repos/{organization}/{repo_name}'
        team_data = {'permission': role}

        response = github_request('PUT', team_url, data=team_data)
        if response.status_code == 204:
            print(f'Team {team} added with {role} access successfully!')
        else:
            print(f'Failed to add team {team}: {response.json()}')


# Main workflow function
def main():
    repo_name = input("Enter the name of the repository to create (use dash between spaces e.g. py-azure-billing): ")
    branches = ['develop', 'test', 'uat', 'main']

    # 1. Create the repository
    repo_info = create_repository(repo_name)

    # 2. Get the SHA of the develop branch
    branch_sha_url = f'https://api.github.com/repos/{organization}/{repo_name}/git/ref/heads/develop'
    response = github_request('GET', branch_sha_url)
    if response.status_code == 200:
        branch_sha = response.json()['object']['sha']
    else:
        print(f'Failed to get SHA for branch creation: {response.json()}')
        exit(1)

    # 3. Create the branches
    create_branches(repo_name, branches, branch_sha)

    # 4. Prompt the user if they want to upload a .gitignore file
    upload_gitignore_response = input("Do you want to upload a .gitignore file? (y/n): ").strip().lower()

    if upload_gitignore_response == 'y':
        # Ask for the .gitignore file path
        gitignore_path = input("Enter the full path to your .gitignore file: ").strip()
        upload_gitignore_to_develop(repo_name, gitignore_path)

        '''
        # Merge develop into all other branches to keep them up to date
        for branch in branches:
            if branch == 'develop':
                continue
            merge_develop_into_branch(repo_name, branch)
            '''
    else:
        print("Skipping .gitignore upload.")


    # 5. Create branch protection rule for main branch
    create_branch_protection(repo_name)

    # 6. Add teams to the repository with specific roles

    teams = {
        f'{dev_team}': 'push',
        f'{ops_team}': 'maintain'
    }

    # Call this function before assigning team permissions to verify correct slugs
    # get_teams(organization)

    assign_team_permissions(repo_name, teams)

    print('All branches, protection rules, and team permissions created successfully!')

if __name__ == "__main__":
    main()


# get_teams(organization)