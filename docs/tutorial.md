# Tutorial: Getting Started with plowman

This step-by-step tutorial will guide you through setting up plowman and deploying your first dotfiles.

## Prerequisites

- Python 3.10 or higher installed
- Basic familiarity with command-line tools
- Some configuration files you want to manage

## Step 1: Install plowman

Install plowman using uv (recommended):

```console
$ uv tool install plowman
```

Verify the installation:

```console
$ plm --version
plowman 0.3.1
```

If you don't have uv, see the [Installation Guide](./installation.md) for alternative methods.

## Step 2: Create Directory Structure

Create a directory for your dotfiles:

```console
$ mkdir -p ~/dotfiles/{bash,nvim,git}
```

This creates a structure like:

```
~/dotfiles/
├── bash/
├── nvim/
└── git/
```

Each subdirectory (called a "granary") will contain related configuration files.

## Step 3: Add Your First Dotfiles

Let's start with a simple `.bashrc` file. Create it in the bash granary:

```console
$ cat > ~/dotfiles/bash/.bashrc << 'EOF'
# My bash configuration

# Aliases
alias ll='ls -la'
alias gs='git status'

# Environment variables
export EDITOR=nvim
export HISTSIZE=10000
EOF
```

Add a simple git config:

```console
$ cat > ~/dotfiles/git/.gitconfig << 'EOF'
[user]
    name = Your Name
    email = your.email@example.com

[core]
    editor = nvim

[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
EOF
```

## Step 4: Write Your First Configuration

Create the plowman configuration directory and file:

```console
$ mkdir -p ~/.config/plowman
```

Create `~/.config/plowman/config.yaml`:

```yaml
estates:
  ~/dotfiles:
    granaries:
      - bash
      - git
```

This tells plowman:
- Look in `~/dotfiles` for your dotfile repositories
- Deploy files from the `bash` and `git` subdirectories
- No template variables needed yet (we'll add those later)

## Step 5: Preview with Dry-Run

Before making any changes, use dry-run mode to see what would happen:

```console
$ plm sow --dry-run
☑️ Would copy /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
☑️ Would copy /home/user/dotfiles/git/.gitconfig to /home/user/.gitconfig
```

This shows:
- Which files would be copied
- Source and destination paths
- No actual changes are made

Dry-run is always recommended before your first deployment!

## Step 6: Deploy Your Dotfiles

Now deploy for real:

```console
$ plm sow
```

You should see output like:

```
☑️ Copying /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
☑️ Copying /home/user/dotfiles/git/.gitconfig to /home/user/.gitconfig
```

Verify the files were deployed:

```console
$ ls -la ~/.bashrc ~/.gitconfig
-rw-r--r-- 1 user user 123 Jun 24 10:00 /home/user/.bashrc
-rw-r--r-- 1 user user 234 Jun 24 10:00 /home/user/.gitconfig
```

Check the content:

```console
$ cat ~/.bashrc
# My bash configuration

# Aliases
alias ll='ls -la'
alias gs='git status'

# Environment variables
export EDITOR=nvim
export HISTSIZE=10000
```

## Step 7: Check the Estate File

plowman created an estate file to track deployed files:

```console
$ cat ~/dotfiles/.plowman/estate.yml
files:
  - .bashrc
  - .gitconfig
```

This file:
- Tracks which files plowman manages
- Enables automatic cleanup of orphaned files
- Is automatically updated on each run

⚠️ **Don't edit this file manually.**

## Step 8: Add Template Variables

Now let's make our configuration dynamic using Jinja2 templates.

First, update your config to include variables:

```yaml
# ~/.config/plowman/config.yaml
estates:
  ~/dotfiles:
    granaries:
      - bash
      - git
    variables:
      username: alice
      email: alice@example.com
      editor: nvim
```

Create a template file. Rename `.gitconfig` to `.gitconfig.j2` and use variables:

```console
$ mv ~/dotfiles/git/.gitconfig ~/dotfiles/git/.gitconfig.j2
```

Edit the template:

```jinja2
# ~/dotfiles/git/.gitconfig.j2
[user]
    name = {{ username }}
    email = {{ email }}

[core]
    editor = {{ editor }}

[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
```

Mark it as a template by creating `.plowman/plowman.yml`:

```console
$ mkdir -p ~/dotfiles/.plowman
```

```yaml
# ~/dotfiles/.plowman/plowman.yml
git:
  templates:
    - .gitconfig.j2
```

This tells plowman that `.gitconfig.j2` should be processed as a Jinja2 template.

## Step 9: Deploy with Templates

Preview the changes:

```console
$ plm sow --dry-run -v
☑️ Would copy /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
☑️ Would copy /home/user/dotfiles/git/.gitconfig.j2 to /home/user/.gitconfig
```

Note that `.gitconfig.j2` will be deployed as `.gitconfig` (the `.j2` extension is removed).

Deploy for real:

```console
$ plm sow
☑️ Copying /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
☑️ Copying /home/user/dotfiles/git/.gitconfig.j2 to /home/user/.gitconfig
```

Verify the template was rendered:

```console
$ cat ~/.gitconfig
[user]
    name = alice
    email = alice@example.com

[core]
    editor = nvim

[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
```

The variables have been substituted!

## Step 10: Use Verbose Mode to See Diffs

See exactly what changed with verbose mode:

```console
$ plm sow -vv
☑️ Copying /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
    @@ -1,5 +1,5 @@
     # My bash configuration
     
     # Aliases
    -alias ll='ls -l'
    +alias ll='ls -la'
     alias gs='git status'
     
     # Environment variables
☑️ Copying /home/user/dotfiles/git/.gitconfig.j2 to /home/user/.gitconfig
```

The diff shows:
- Lines starting with `-` are being removed
- Lines starting with `+` are being added
- Context lines show surrounding content

## Step 11: Make Changes and Re-deploy

Update your `.bashrc` in the granary:

```console
$ cat >> ~/dotfiles/bash/.bashrc << 'EOF'

# Additional aliases
alias gp='git push'
alias gl='git pull'
EOF
```

Re-deploy:

```console
$ plm sow -v
☑️ Copying /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
```

Notice that only the changed file was deployed. plowman uses SHA256 hashing to skip unchanged files, making re-deployment fast.

## Step 12: Remove a File and See Cleanup

Remove a file from your granary:

```console
$ rm ~/dotfiles/git/.gitconfig.j2
```

Update the per-path config to remove the template reference:

```yaml
# ~/dotfiles/.plowman/plowman.yml
git:
  templates: []  # No templates now
```

Run plowman:

```console
$ plm sow -v
🧹 Deleting /home/user/.gitconfig
```

plowman detected that `.gitconfig` is no longer in your configuration and automatically removed it. This keeps your home directory clean and synchronized with your granaries.

## Step 13: Add More Granaries

Add a neovim configuration:

```console
$ mkdir -p ~/dotfiles/nvim
$ cat > ~/dotfiles/nvim/init.vim << 'EOF'
" Neovim configuration
set number
set relativenumber
set tabstop=4
set shiftwidth=4
set expandtab
EOF
```

Update your main config:

```yaml
# ~/.config/plowman/config.yaml
estates:
  ~/dotfiles:
    granaries:
      - bash
      - git
      - nvim  # Added!
    variables:
      username: alice
      email: alice@example.com
      editor: nvim
```

Deploy:

```console
$ plm sow -v
☑️ Copying /home/user/dotfiles/nvim/init.vim to /home/user/.config/nvim/init.vim
```

Notice that plowman automatically created the `~/.config/nvim/` directory structure.

## Step 14: Advanced Template Example

Create a more complex template with conditionals:

```jinja2
# ~/dotfiles/bash/.bash_profile.j2
# Bash profile for {{ username }}

# Platform-specific settings
{% if os == "darwin" %}
# macOS specific
export PATH="/usr/local/bin:$PATH"
export HOMEBREW_PREFIX="/usr/local"
{% elif os == "linux" %}
# Linux specific
export PATH="$HOME/.local/bin:$PATH"
{% endif %}

# User settings
export USER="{{ username }}"
export EMAIL="{{ email }}"
export EDITOR="{{ editor }}"

# Load .bashrc if it exists
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi
```

Update config with OS variable:

```yaml
estates:
  ~/dotfiles:
    granaries:
      - bash
      - git
      - nvim
    variables:
      username: alice
      email: alice@example.com
      editor: nvim
      os: darwin  # Change to "linux" on Linux systems
```

Mark it as a template:

```yaml
# ~/dotfiles/.plowman/plowman.yml
bash:
  templates:
    - .bash_profile.j2
```

Deploy:

```console
$ plm sow -v
☑️ Copying /home/user/dotfiles/bash/.bash_profile.j2 to /home/user/.bash_profile
```

Check the rendered result:

```console
$ cat ~/.bash_profile
# Bash profile for alice

# Platform-specific settings
# macOS specific
export PATH="/usr/local/bin:$PATH"
export HOMEBREW_PREFIX="/usr/local"

# User settings
export USER="alice"
export EMAIL="alice@example.com"
export EDITOR="nvim"

# Load .bashrc if it exists
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi
```

## Next Steps

Congratulations! You've successfully:
- ✅ Installed plowman
- ✅ Created a dotfile repository structure
- ✅ Configured granaries and variables
- ✅ Deployed plain files and templates
- ✅ Used dry-run and verbose modes
- ✅ Seen automatic cleanup in action
- ✅ Created advanced templates with conditionals

### Continue Learning: Harvest Command

Now that you know how to deploy configs with `sow`, learn how to collect changes back with `harvest`:

#### Step 15: Understanding Harvest

The `harvest` command does the opposite of `sow` - it collects changed files from your home directory back into your granaries.

**When to use harvest:**
- You manually edited a config file in HOME (not through your dotfiles repo)
- You want to sync changes made on one machine back to your central dotfiles repo
- You're setting up a new machine and need to collect existing configs

#### Step 16: Add Granary Names for Harvest

To use the `-a/--add-to-estate` feature, add names to your granaries:

```yaml
# ~/dotfiles/.plowman/plowman.yml
bash:
  name: myshell  # Add this line
  templates:
    - .bashrc.j2

git:
  name: mygit  # Add this line
  templates:
    - .gitconfig.j2
```

#### Step 17: Make Manual Changes

Let's say you edited `.bashrc` directly instead of through your dotfiles repo:

```console
$ echo "# New alias" >> ~/.bashrc
$ echo "alias docker='sudo docker'" >> ~/.bashrc
```

#### Step 18: Preview Changes with Dry-Run

See what would be harvested:

```console
$ plm harvest --dry-run -v
☑️ Would harvest /home/user/.bashrc to /home/user/dotfiles/bash/.bashrc
```

See detailed diffs:

```console
$ plm harvest --dry-run -vv
☑️ Would harvest /home/user/.bashrc to /home/user/dotfiles/bash/.bashrc
    @@ -8,3 +8,5 @@
     export HISTSIZE=10000
    +
    +# New alias
    +alias docker='sudo docker'
```

#### Step 19: Harvest the Changes

Collect the changes back to your granary:

```console
$ plm harvest -v
☑️ Harvesting /home/user/.bashrc to /home/user/dotfiles/bash/.bashrc
```

Verify the granary was updated:

```console
$ tail -3 ~/dotfiles/bash/.bashrc

# New alias
alias docker='sudo docker'
```

#### Step 20: Commit to Version Control

Now commit the harvested changes:

```console
$ cd ~/dotfiles
$ git status
$ git add bash/.bashrc
$ git commit -m "Add docker alias from manual edit"
$ git push
```

#### Step 21: Add New Files with --add-to-estate

Suppose you created a new config file manually:

```console
$ cat > ~/.tmux.conf << 'EOF'
# TMUX configuration
set -g mouse on
set -g status-bg blue
EOF
```

Add it to estate tracking and harvest it in one command:

```console
$ plm harvest -a myshell::/home/user/.tmux.conf -v
☑️ Harvesting /home/user/.tmux.conf to /home/user/dotfiles/bash/.tmux.conf
```

This:
1. Adds `/home/user/.tmux.conf` to estate tracking under the `myshell` granary
2. Copies it to `~/dotfiles/bash/.tmux.conf`
3. Updates the estate file

Verify:

```console
$ ls ~/dotfiles/bash/.tmux.conf
/home/user/dotfiles/bash/.tmux.conf

$ cat ~/dotfiles/.plowman/estate.yml
files:
  - .bashrc
  - .tmux.conf  # Newly added!
```

#### Step 22: Sync Across Machines

Harvest makes it easy to sync configs between machines:

**On Machine A (where you made changes):**

```console
# Harvest all manual changes
$ plm harvest -v

# Commit and push
$ cd ~/dotfiles
$ git add .
$ git commit -m "Sync from Machine A"
$ git push
```

**On Machine B:**

```console
# Pull latest changes
$ cd ~/dotfiles
$ git pull

# Deploy to Machine B
$ plm sow -v
```

Now both machines have the same configuration!

#### Step 23: Template Files and Harvest

Harvest handles template files automatically:

```console
# HOME has: ~/.gitconfig (rendered, no .j2)
# Granary has: ~/dotfiles/git/.gitconfig.j2 (template source)

# Edit the rendered file
$ echo "[diff]\n    tool = meld" >> ~/.gitconfig

# Harvest will update the .j2 template
$ plm harvest -v
☑️ Harvesting /home/user/.gitconfig to /home/user/dotfiles/git/.gitconfig.j2
```

⚠️ **Note:** When harvesting template files, you're copying the *rendered* content back to the template. If the template contains Jinja2 variables, they will be replaced with actual values. Consider editing the `.j2` file directly in your granary instead.

Continue learning:
- Read the complete [Usage Guide](./usage/) for all features
- Explore the [Configuration Reference](./configuration.md) for advanced options
- Check the [FAQ](./faq.md) for common questions
- See [Troubleshooting](./troubleshooting.md) for help with issues

## Tips

### Version Control Your Dotfiles

Store your granaries in Git:

```console
$ cd ~/dotfiles
$ git init
$ git add .
$ git commit -m "Initial dotfiles setup"
```

Add estate files to `.gitignore`:

```gitignore
# ~/dotfiles/.gitignore
.plowman/estate.yml
```

### Use Multiple Machines

Sync your dotfiles across machines:

1. Push to GitHub/GitLab
2. Clone on new machine
3. Install plowman
4. Run `plm sow`

### Backup Before Major Changes

```console
$ cp ~/.bashrc ~/.bashrc.backup
$ plm sow
```

Or just use dry-run first:

```console
$ plm sow --dry-run -vv
```

### Organize by Category

Keep related configs together:

```
dotfiles/
├── shell/      # Shell configs
├── editor/     # Editor configs
├── git/        # Git configs
├── ssh/        # SSH configs
└── tools/      # Other tools
```

Happy dotfile farming! 🌾
