import sys

from .oauth2 import OAuth2Service
from .config import config


class Github(OAuth2Service):
    client = config['github']['client']
    secret = config['github']['secret']
    autho_url = 'https://github.com/login/oauth/authorize'
    token_url = 'https://github.com/login/oauth/access_token'
    api_url = 'https://api.github.com/{service}'
    token_file = '.github-auth'
    scope = 'public_repo,read:org'

    def __init__(self):
        super(Github, self).__init__(Github)
        self.groups = None
        self.repos = None

    def reponame(self, repo):
        return repo['full_name']

    def groupname(self, group):
        return group['login']

    def get_repos(self, force=False):
        if self.repos and not force:
            return self.repos

        print('listing github repositories...', file=sys.stderr)
        service_url = Github.api_url.format(service='user/repos')

        params = {'page': 1}
        projects = self.get(service_url, params=params).json()
        next_projects = projects
        while len(next_projects) > 0:
            params['page'] += 1
            next_projects = self.get(service_url, params=params).json()
            projects += next_projects

        self.repos = dict([(self.reponame(p), p) for p in projects])
        return self.repos

    def get_groups(self, force=False):
        if self.groups and not force:
            return self.groups

        print('listing github groups...', file=sys.stderr)
        service_url = Github.api_url.format(service='user/orgs')

        params = {'page': 1}
        groups = self.get(service_url, params=params).json()
        next_groups = groups
        while len(next_groups) > 0:
            params['page'] += 1
            next_groups = self.get(service_url, params=params).json()
            groups += next_groups

        self.groups = dict([(self.groupname(g), g) for g in groups])
        return self.groups


if __name__ == '__main__':
    github = Github()

    print('github groups:')
    for k, v in sorted(github.get_groups().items()):
        print(' -', k, v)

    print('github repos:')
    for k, v in sorted(github.get_repos().items()):
        print(' -', k, v)
