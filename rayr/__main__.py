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


def sync_repo(name, r, github, gitlab, bitbkt):
    if r['private']:
        return

    group = r['owner']['login']
    github_repo = name
    gitlab_repo = name.replace('/.', '/dot-').replace('.', '-')
    bitbkt_repo = name

    description = []
    if 'description' in r and r['description']:
        description.append(r['description'])
    if 'html_url' in r and r['html_url']:
        description.append('Mirror of %s.' % r['html_url'])
    if 'homepage' in r and r['homepage']:
        description.append('%s' % r['homepage'])
    description = ' '.join(description)

    if (gitlab is not None and
       gitlab_repo.lower() not in gitlab.get_repos() and
       group in gitlab.get_groups()):
        gitlab.create_repo(group, gitlab_repo,
                           description=description, private=r['private'])

    if (bitbkt is not None and
       bitbkt_repo.lower() not in bitbkt.get_repos() and
       group in bitbkt.get_groups()):
        bitbkt.create_repo(bitbkt_repo,
                           description=description, private=r['private'],
                           language=r['language'] or '')

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
    github = Github() if config['github']['enabled'] else None
    gitlab = Gitlab() if config['gitlab']['enabled'] else None
    bitbkt = Bitbucket() if config['bitbucket']['enabled'] else None

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
