#!/usr/bin/env python
# coding=utf-8

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from subprocess import check_output, call
import urllib2
import json
import sys
import subprocess
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

if __name__ == '__main__':

    parser = ArgumentParser(
        description=(
            "Run a bunch of boilerplate commands"
            " to sync your local clone to its parent github repo."
        ),
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-b', '--branch', help='name of the branch to sync',
                        type=str, default='master', required=False)
    parser.add_argument('-p', '--protocol', help='git protocol to use',
                        type=str, choices=['git', 'html'], default='html',
                        required=False)
    args = parser.parse_args()
    branch = args.branch
    protocol = args.protocol

    print("Starting sync...", "\n")

    CURRENT_REPO_CMD = ['git', 'ls-remote', '--get-url', 'origin']
    ADD_REMOTE_CMD = ['git', 'remote', 'add', 'upstream']
    REMOVE_CURRENT_URL_CMD = ['git', 'remote', 'remove', 'upstream']
    CHECK_REMOTES_CMD = ['git', 'remote', '-v']
    FETCH_UPSTREAM_CMD = ['git', 'fetch', 'upstream']
    CHECKOUT_BRANCH_CMD = ['git', 'checkout', '{}'.format(branch)]
    MERGE_UPSTREAM_CMD = ['git', 'merge', 'upstream/{}'.format(branch)]
    CHECK_UPSTREAM_CMD = ['git', 'ls-remote', '--get-url', 'upstream']

    try:
        repo_url = check_output(CURRENT_REPO_CMD)
        print("Getting repo's url...")
        print("Syncing repo:", repo_url)

        url_segments = repo_url.split("github.com/")
        path = url_segments[1]
        user, repo = path.split("/")
        repo = repo.split(".git")

        print("Checking the fork's parent url...", "\n")
        url = "https://api.github.com/repos/{}/{}".format(user, repo[0])
        req = urllib2.urlopen(url)
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

        print("Merging upstream and {}".format(branch), "\n")
        check_output(CHECKOUT_BRANCH_CMD)
        call(MERGE_UPSTREAM_CMD)
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
                  (e.cmd == MERGE_UPSTREAM_CMD or e.cmd == CHECKOUT_BRANCH_CMD)):
                print("Didn't merge. Reason:", e.output)
        print("Game Over.")
