#!/usr/bin/env python3
# coding=utf-8


import os
import sys
import json
import pathlib
import shutil
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from subprocess import check_output, call
from urllib.request import urlopen
from ruamel.yaml import YAML


def repo_relist(repo_list):
    new_repo_list = []
    for repo_dict in repo_list:
        repo = {}
        repo_url = repo_dict['url']
        url_segments = repo_url.split("github.com/")
        repo['url'] = repo_url
        repo['user'], name = url_segments[1].split("/")
        repo['name'] = name.split(".git")[0]
        repo['branches'] = repo_dict['branches']
        new_repo_list.append(repo)

    return new_repo_list


def github_clone(url):
    CLONE_REPO_CMD = ['git', 'clone', f'{url}']
    try:
        print(f"Cloning repo: {url}", "\n")
        call(CLONE_REPO_CMD)
        print("")
    except Exception as e:
        e_type = sys.exc_info()[0].__name__
        if (e_type != 'NameError'):
            print("The following error happened:", e, "\n")
            if (e_type == 'CalledProcessError' and
                    (e.cmd in [CLONE_REPO_CMD])):
                print("Didn't clone. Reason:", e.output)
        print("Game Over.")


def github_sync(branch, protocol='html'):

    print("Starting sync...", "\n")

    CURRENT_REPO_CMD = ['git', 'ls-remote', '--get-url', 'origin']
    ADD_REMOTE_CMD = ['git', 'remote', 'add', 'upstream']
    REMOVE_CURRENT_URL_CMD = ['git', 'remote', 'remove', 'upstream']
    CHECK_REMOTES_CMD = ['git', 'remote', '-v']
    FETCH_UPSTREAM_CMD = ['git', 'fetch', 'upstream']
    CHECKOUT_BRANCH_CMD = ['git', 'checkout', f'{branch}']
    MERGE_UPSTREAM_CMD = ['git', 'merge', f'upstream/{branch}']
    CHECK_UPSTREAM_CMD = ['git', 'ls-remote', '--get-url', 'upstream']
    PUSH_ORIGIN_CMD = ['git', 'push', 'origin', f'{branch}']

    try:
        repo_url = check_output(CURRENT_REPO_CMD, encoding='utf-8')
        print("Getting repo's url...")
        print(f"Syncing repo: {repo_url} branch: {branch}")

        url_segments = repo_url.split("github.com/")
        path = url_segments[1]
        user, repo = path.split("/")
        repo = repo.split(".git")

        print("Checking the fork's parent url...", "\n")
        url = f"https://api.github.com/repos/{user}/{repo[0]}"
        req = urlopen(url)
        res = json.load(req)
        parent_git_url = res['parent']['git_url']
        parent_html_url = res['parent']['html_url']
        protocol_git = parent_git_url.split("/")
        protocol_html = parent_html_url.split("/")

        if (protocol_git[0] == 'git:' and protocol_html[0] == 'https:'):
            if (protocol in ['git']):
                print("Will add remote to parent repo:", parent_git_url, "\n")
                ADD_REMOTE_CMD.append(parent_git_url)
                call(REMOVE_CURRENT_URL_CMD)
            elif (protocol in ['html']):
                print("Will add remote to parent repo:", parent_html_url, "\n")
                call(REMOVE_CURRENT_URL_CMD)
                ADD_REMOTE_CMD.append(parent_html_url)
        call(ADD_REMOTE_CMD)
        print("")

        print("Checking remotes...", "\n")
        call(CHECK_REMOTES_CMD)
        print("")

        print("Fetching upstream...", "\n")
        call(FETCH_UPSTREAM_CMD)
        print("")

        print(f"Merging upstream and {branch}", "\n")
        check_output(CHECKOUT_BRANCH_CMD, encoding='utf-8')
        call(MERGE_UPSTREAM_CMD)
        print("")

        print(f"Pushing to origin...", "\n")
        call(PUSH_ORIGIN_CMD)
        print("Syncing done.")

    except Exception as e:
        e_type = sys.exc_info()[0].__name__
        if (e_type != 'NameError'):
            print("The following error happened:", e, "\n")
            if (e_type == 'CalledProcessError' and
                hasattr(e, 'cmd') and
                    e.cmd == CURRENT_REPO_CMD):
                print("Are you sure you are on the git repo folder?", "\n")
            elif (e_type == 'IndexError' and
                  e.message == 'list index out of range'):
                print(
                    "Sorry, couldn't get the user and repo names from the Git config.", "\n")
            elif (e_type == 'KeyError' and
                  e.message == 'parent'):
                print("Are you sure the repo is a fork?")
            elif (e_type == 'CalledProcessError' and
                  (e.cmd in [MERGE_UPSTREAM_CMD, CHECKOUT_BRANCH_CMD, PUSH_ORIGIN_CMD])):
                print("Didn't merge. Reason:", e.output)
        print("Game Over.")


if __name__ == '__main__':

    parser = ArgumentParser(
        description=(
            "Run a bunch of boilerplate commands"
            "to sync your local clone to its parent github repo."
        ),
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-y', '--yaml', help='name of the yaml file containing repos and branches to sync',
                        type=str, default='gsync_forks.yaml', required=False)
    args = parser.parse_args()

    yaml_file = args.yaml

    yaml = YAML(typ='safe')
    with open(yaml_file, 'r') as fh:
        repo_list = yaml.load(fh)

    repo_list = repo_relist(repo_list)

    for repo in repo_list:
        # Remove stale clones
        if pathlib.Path(repo['name']).exists():
            print(f"Directoty {repo['name']} exists, cleaning!")
            shutil.rmtree(repo['name'])

        # Clone the repo and cd into the directory
        github_clone(repo['url'])
        os.chdir(repo['name'])

        # Sync and push branches
        for branch in repo['branches']:
            github_sync(branch)
