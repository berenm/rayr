import sys

from .oauth2 import OAuth2Service
from .config import config


class Github(OAuth2Service):
    enabled = config['github']['enabled']
    private = config['github']['private']
    client = config['github']['client']
    secret = config['github']['secret']
    redir_url = 'http://127.0.0.1:8080'
    autho_url = 'https://github.com/login/oauth/authorize'
    token_url = 'https://github.com/login/oauth/access_token'
    api_url = 'https://api.github.com/{service}'
    token_file = '.github-auth'
    scopes = ['read:org', 'repo']

    def __init__(self):
        super(Github, self).__init__(Github)
        self.groups = None
        self.repos = None

    def reponame(self, repo):
        return repo['full_name']

    def is_private(self, repo):
        return repo['private']

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

        self.repos = dict([(self.reponame(p), p) for p in projects
                           if Github.private or not self.is_private(p)])
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
    for k, _ in sorted(github.get_groups().items()):
        print(' -', k)

    repos = github.get_repos()
    print('github public repos:')
    for k, v in sorted(repos.items()):
        if github.is_private(v):
            continue
        print(' -', k)

    print('github private repos:')
    for k, v in sorted(repos.items()):
        if not github.is_private(v):
            continue
        print(' -', k)
