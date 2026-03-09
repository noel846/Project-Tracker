# -keep-Project-Tracker

A project tracker to help keep things organized.

---

## How to Push from VS Code

If you're getting an error when trying to push from VS Code, follow these steps:

### Step 1 — Set the correct remote URL

Open a terminal (in VS Code: `Ctrl+`` ` or `Terminal > New Terminal`) and run:

```bash
git remote set-url origin https://github.com/noel846/-keep-Project-Tracker.git
```

Then verify it worked:

```bash
git remote -v
# Should show:
# origin  https://github.com/noel846/-keep-Project-Tracker.git (fetch)
# origin  https://github.com/noel846/-keep-Project-Tracker.git (push)
```

### Step 2 — Make sure you're signed in to GitHub in VS Code

1. Click the **Accounts** icon (bottom-left of VS Code, looks like a person)
2. Click **Sign in with GitHub**
3. Follow the browser prompts to authorize VS Code

### Step 3 — Push your code

In VS Code:
- Open the **Source Control** panel (`Ctrl+Shift+G`)
- Stage your changes (click the `+` next to files)
- Write a commit message and click the checkmark ✓ to commit
- Click **Sync Changes** or **Push**

Or from the terminal:

```bash
git add .
git commit -m "Your commit message here"
git push -u origin main
```

### Common Errors

| Error | Fix |
|-------|-----|
| `Authentication failed` | Sign in to GitHub in VS Code (Step 2 above) |
| `remote: Repository not found` | Check the remote URL is correct (Step 1 above) |
| `rejected — non-fast-forward` | Run `git pull origin main` first, then push again |
| `src refspec main does not match` | Your branch might be called `master` — try `git push -u origin master` |

---

## Quick Start (cloning fresh)

```bash
git clone https://github.com/noel846/-keep-Project-Tracker.git
cd -keep-Project-Tracker
```
