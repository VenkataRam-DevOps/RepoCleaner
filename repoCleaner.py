import os
import datetime
from github import Github

# Fetch the GitHub token from the environment variable
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")  # Ensure this matches the secret name you used

# Fetch the user input for deletion from the environment variable
delete_all_branches_input = os.getenv("DELETE_ALL_BRANCHES", "no")  # Default to "no" if not provided
selected_branches_input = os.getenv("DELETE_SELECTED_BRANCHES", "")  # Get branches to delete from an environment variable

# Ensure the token is available
if not GITHUB_TOKEN:
    print("Error: GitHub token not found. Please ensure it is set as an environment variable.")
    raise ValueError("GitHub token is not provided. Make sure to set the MY_GITHUB_TOKEN secret.")

# Initialize the GitHub client with the token
def initialize_github():
    return Github(GITHUB_TOKEN)

# Read repository URLs from the file
def read_repos_from_file(file_name="masterRepoList.txt"):
    with open(file_name, "r") as file:
        repos = [line.strip() for line in file.readlines()]
    return repos

# Get branches for a specific repository
def get_repo_branches(github_client, repo_url):
    repo_name = repo_url.split('/')[-1]
    user_name = repo_url.split('/')[-2]
    
    repo = github_client.get_user(user_name).get_repo(repo_name)
    return repo.get_branches()

# Check if a branch is stale (older than 1 year)
def is_stale_branch(commit_date, threshold_days=365):
    today = datetime.datetime.now()
    age = today - commit_date
    return age.days > threshold_days

# Get user approval for deleting branches (modified to use environment variables)
def get_user_approval_for_deletion(stale_branches):
    print("Stale branches found:")
    for idx, branch in enumerate(stale_branches, 1):
        print(f"{idx}. {branch['name']} (Last commit: {branch['commit_date']})")

    if delete_all_branches_input.lower() == 'yes':
        print("You selected to delete all stale branches.")
        return [branch['name'] for branch in stale_branches]
    elif selected_branches_input:
        print(f"You selected to delete the following branches: {selected_branches_input}")
        return selected_branches_input.split(",")  # Assuming branches are passed as comma-separated string
    else:
        print("You selected to delete only selected branches.")
        print("Skipping deletion as no branches were selected.")
        return []

# Delete branches from the repository
def delete_branches(github_client, repo_url, branches_to_delete):
    repo_name = repo_url.split('/')[-1]
    user_name = repo_url.split('/')[-2]

    repo = github_client.get_user(user_name).get_repo(repo_name)

    for branch in branches_to_delete:
        try:
            ref = repo.get_git_ref(f"heads/{branch}")
            ref.delete()
            print(f"Deleted branch: {branch}")
        except Exception as e:
            print(f"Error deleting branch {branch}: {str(e)}")

# Generate the executive summary after cleanup
def generate_summary(deleted_branches):
    if deleted_branches:
        print("\nExecutive Summary:")
        print("Branches Deleted:")
        for branch in deleted_branches:
            print(f" - {branch}")
    else:
        print("\nNo branches were deleted.")

# Save the progress to a file to track the last processed repository
def save_progress(repo_url):
    with open('progress.txt', 'w') as file:
        file.write(repo_url)

# Load the last processed repository from the progress file
def load_progress():
    if os.path.exists('progress.txt'):
        with open('progress.txt', 'r') as file:
            return file.read().strip()
    return None

# Main function to execute the repoCleaner utility
def repo_cleaner():
    # Initialize GitHub client
    github_client = initialize_github()

    # Read repository URLs
    repos = read_repos_from_file()

    # Check if there's a saved progress to resume
    last_processed_repo = load_progress()
    if last_processed_repo:
        print(f"Resuming from the last processed repository: {last_processed_repo}")
        repos = repos[repos.index(last_processed_repo):]

    # Loop through each repository
    for repo_url in repos:
        print(f"Processing repository: {repo_url}")
        branches = get_repo_branches(github_client, repo_url)

        # Find stale branches
        stale_branches = []
        for branch in branches:
            commit_date = branch.commit.commit.author.date
            if is_stale_branch(commit_date):
                stale_branches.append({
                    "name": branch.name,
                    "commit_date": commit_date
                })
        
        if stale_branches:
            # Ask user for branch deletion approval
            branches_to_delete = get_user_approval_for_deletion(stale_branches)
            delete_branches(github_client, repo_url, branches_to_delete)
            generate_summary(branches_to_delete)

            # Save progress after processing the repository
            save_progress(repo_url)
        else:
            print(f"No stale branches found in {repo_url}\n")
    
    print("repoCleaner completed.")

if __name__ == "__main__":
    repo_cleaner()
