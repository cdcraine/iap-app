# Publish Tiger Engineering Pathway to GitHub from a Mac

This project package is ready for a new repository named `tiger-engineering-pathway` under `cdcraine`. The script below uses GitHub CLI; it does not require you to paste a GitHub token into a file or chat.

## 1. Download and extract

Download the `Tiger-Engineering-Pathway-GitHub-Ready.zip` package and extract it. Open Terminal in the extracted `Tiger-Engineering-Pathway-GitHub-Ready` folder.

One way to enter the folder, if it is in Downloads:

```bash
cd ~/Downloads/Tiger-Engineering-Pathway-GitHub-Ready
```

If the folder was extracted elsewhere, use that actual path instead.

## 2. Install tools and authenticate

```bash
brew install git gh
 gh auth login
 gh auth status
 gh api user --jq .login
```

The last command must print `cdcraine`. Stop if it prints another account.

## 3. Install dependencies and test locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m py_compile app.py database.py tests/test_app.py
pytest -q
```

Then optionally run the app with `python app.py` and open <http://127.0.0.1:5000>.

## 4. Create and push a new private repository

First check whether the repository name is already in use:

```bash
gh repo view cdcraine/tiger-engineering-pathway
```

If GitHub reports that the repository does not exist, create and push it:

```bash
gh repo create cdcraine/tiger-engineering-pathway \
  --private \
  --source=. \
  --remote=origin \
  --push
```

This command creates a new private repository and pushes the current project. **If the repository already exists, do not rerun the create command blindly.** Inspect the existing repository and its branch history first so that no unrelated content is overwritten.

## 5. Push later updates

After editing files in this same local project folder:

```bash
git status
git add .
git commit -m "Update Tiger Engineering Pathway"
git push
```

Review `git status` before committing. The `.gitignore` excludes generated SQLite database files, Python caches, virtual environments, and `.env` secrets. Do not add personal student data or credentials.

## 6. Confirm continuous integration

After the first push, open the repository's **Actions** tab. Wait for `Tiger Engineering Pathway CI` to finish. If a test fails, fix it and push a new commit. Only then should the assignment report a green CI run URL.
