# repoCleaner

`repoCleaner` is a utility that helps clean up stale branches from repositories on GitHub. It automatically identifies branches that haven't had a commit in over a year, prompts the user for deletion approval, and deletes the branches that the user selects.

## Features

- Identifies stale branches in GitHub repositories.
- Allows users to select branches for deletion.
- Provides an executive summary after cleanup.
- Supports error recovery and resume functionality in case of failure.

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/username/repoCleaner.git
   cd repoCleaner
   
2. **Install Dependencies:**
     pip install -r requirements.txt

3. **Create a GitHub Personal Access Token:**

Go to GitHub → Settings → Developer settings → Personal access tokens → Generate new token.
Ensure the token has repo scope

4. **Update the script with your GitHub token:**

In repoCleaner.py, replace your_github_token_here with your generated GitHub token.

5. **Update Masterreposfile**

6. **Run the utility**
7.     python repoCleaner.py
