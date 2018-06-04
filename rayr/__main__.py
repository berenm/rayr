#!/usr/bin/env python3

import os
import sys

from .config import config
from .github import Github
from .gitlab import Gitlab
from .bitbucket import Bitbucket

from subprocess import call


def sync_group(name, description, github, gitlab, bitbkt):
    if gitlab is not None:
        if name not in gitlab.get_groups():
            gitlab.create_group(name, description)
        else:
            gitlab.update_group(name, description=description)


def sync_repo(name, repo, github, gitlab, bitbkt):
    if repo['private']:
        return

    group = repo['owner']['login']
    github_repo = name
    gitlab_repo = name.replace('/.', '/_.')
    bitbkt_repo = name

    description = []
    if 'description' in repo and repo['description']:
        description.append(repo['description'])
    if 'html_url' in repo and repo['html_url']:
        description.append('Mirror of %s.' % repo['html_url'])
    if 'homepage' in repo and repo['homepage']:
        description.append('%s' % repo['homepage'])
    description = ' '.join(description)

    if (gitlab is not None and
       gitlab_repo.lower() not in gitlab.get_repos() and
       group in gitlab.get_groups()):
        gitlab.create_repo(group, gitlab_repo,
                           description=description, private=repo['private'])

    if (bitbkt is not None and
       bitbkt_repo.lower() not in bitbkt.get_repos() and
       group in bitbkt.get_groups()):
        bitbkt.create_repo(bitbkt_repo,
                           description=description, private=repo['private'],
                           language=repo['language'] or '')

    if not os.path.exists(github_repo):
        call('git clone --mirror git@github.com:{repo}.git {repo}'
             .format(repo=github_repo), shell=True)
        call('git --git-dir={repo} remote rm origin'
             .format(repo=github_repo), shell=True)
        call(('git --git-dir={repo} remote add --mirror=fetch '
              'github git@github.com:{github}.git')
             .format(repo=github_repo, github=github_repo), shell=True)

        if gitlab is not None:
            call(('git --git-dir={repo} remote add --mirror=push '
                  'gitlab git@gitlab.com:{gitlab}.git')
                 .format(repo=github_repo, gitlab=gitlab_repo.lower()),
                 shell=True)

        if bitbkt is not None:
            call(('git --git-dir={repo} remote add --mirror=push '
                  'bitbkt git@bitbucket.org:{bitbkt}.git')
                 .format(repo=github_repo, bitbkt=bitbkt_repo.lower()),
                 shell=True)

    call(('git --git-dir={repo} remote set-url '
          'github git@github.com:{github}.git')
         .format(repo=github_repo, github=github_repo), shell=True)

    if gitlab is not None:
        call(('git --git-dir={repo} remote set-url '
              'gitlab git@gitlab.com:{gitlab}.git')
             .format(repo=github_repo, gitlab=gitlab_repo.lower()),
             shell=True)

    if bitbkt is not None:
        call(('git --git-dir={repo} remote set-url '
              'bitbkt git@bitbucket.org:{bitbkt}.git')
             .format(repo=github_repo, bitbkt=bitbkt_repo.lower()),
             shell=True)

    call('git --git-dir={repo} fetch github --prune'.format(repo=github_repo),
         shell=True)

    if gitlab is not None:
        call('git --git-dir={repo} push gitlab --mirror'
             .format(repo=github_repo),
             shell=True)

    if bitbkt is not None:
        call('git --git-dir={repo} push bitbkt --mirror'
             .format(repo=github_repo),
             shell=True)


if __name__ == '__main__':
    github = Github() if Github.enabled else None
    gitlab = Gitlab() if Gitlab.enabled else None
    bitbkt = Bitbucket() if Bitbucket.enabled else None

    if github is None:
        exit(0)

    for k, v in github.get_groups().items():
        if k in config['exclude']['groups']:
            continue

        print('syncing group github/{}...'.format(k), file=sys.stderr)
        sync_group(k, v['description'], github, gitlab, bitbkt)

    for k, v in github.get_repos().items():
        if k.split('/')[0] in config['exclude']['groups']:
            continue
        if k in config['exclude']['repos']:
            continue

        print('syncing repo github/{}...'.format(k), file=sys.stderr)
        sync_repo(k, v, github, gitlab, bitbkt)
