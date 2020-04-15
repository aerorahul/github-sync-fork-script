github-sync-fork-script
=======================

Python script to sync your github fork to its parent repository.

## Installation

* Clone the repository.
* Put the script gsync.py on your path. In Windows you would probably place it on the root of your python folder (which in most cases is already in the path), somewhere like `C:\Python27`. That way the script would be callable from any folder.

## Usage

* Clone your repo and cd into its folder. Copy `gsync.py` to a folder in your `PATH` e.g. `$HOME/bin`.

* Run gsync.py
```
$> gsync.py --help
usage: gsync.py [-h] [-b BRANCH] [-p {git,html}]

Run a bunch of boilerplate commands to sync your local clone to its parent
github repo.

optional arguments:
  -h, --help            show this help message and exit
  -b BRANCH, --branch BRANCH
                        name of the branch to sync (default: master)
  -p {git,html}, --protocol {git,html}
                        git protocol to use (default: html)
```

* Cake

The Script has some basic error handling. It will catch if the repo is not a fork (in that case there won't be anything to sync), if you are not in the folder of a git repo, etc.

## How does it work?

The script basically follows the github syncing instructions [page](https://help.github.com/articles/syncing-a-fork), but saving you the need to search for the parent repo's git url (which the script gets automatically from github) and typing the 100+ characters of the 4+ needed git commands.
