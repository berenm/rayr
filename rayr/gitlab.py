import sys

from .oauth2 import OAuth2Service
from .config import config


class Gitlab(OAuth2Service):
    enabled = config['gitlab']['enabled']
    private = config['gitlab']['private']
    client = config['gitlab']['client']
    secret = config['gitlab']['secret']
    redir_url = 'http://127.0.0.1:8080'
    autho_url = 'https://gitlab.com/oauth/authorize'
    token_url = 'https://gitlab.com/oauth/token'
    api_url = 'https://gitlab.com/api/v4/{service}'
    token_file = '.gitlab-auth'
    scopes = []

    def __init__(self):
        super(Gitlab, self).__init__(Gitlab)
        self.groups = None
        self.repos = None

    def reponame(self, repo):
        return repo['path_with_namespace']

    def is_private(self, repo):
        return not repo['public']

    def groupname(self, group):
        return group['path']

    def get_repos(self, force=False):
        if self.repos and not force:
            return self.repos

        print('listing gitlab repositories...', file=sys.stderr)
        service_url = Gitlab.api_url.format(service='projects')

        params = {'membership': 'true', 'simple': 'true', 'page': 1}
        projects = self.get(service_url, params=params).json()
        next_projects = projects
        while len(next_projects) > 0:
            params['page'] += 1
            next_projects = self.get(service_url, params=params).json()
            projects += next_projects

        self.repos = dict([(self.reponame(p), p) for p in projects
                           if Gitlab.private or not self.is_private(p)])
        return self.repos

    def get_groups(self, force=False):
        if self.groups and not force:
            return self.groups

        print('listing gitlab groups...', file=sys.stderr)
        service_url = Gitlab.api_url.format(service='namespaces')

        params = {'page': 1}
        groups = self.get(service_url, params=params).json()
        next_groups = groups
        while len(next_groups) > 0:
            params['page'] += 1
            next_groups = self.get(service_url, params=params).json()
            groups += next_groups

        self.groups = dict([(self.groupname(g), g) for g in groups])
        return self.groups

    def create_repo(self, group, name, **kwargs):
        groups = self.get_groups()
        self.get_repos()

        print('creating gitlab/{}...'.format(name), file=sys.stderr)
        service_url = Gitlab.api_url.format(service='projects')

        params = {
            'name': name.replace(group + '/', ''),
            'namespace_id': groups[group]['id'],
            'description': kwargs.get('description', ''),
            'issues_enabled': str(False).lower(),
            'merge_requests_enabled': str(False).lower(),
            'wiki_enabled': str(False).lower(),
            'snippets_enabled': str(False).lower(),
            'public': str(not kwargs.get('private', False)).lower(),
        }
        self.repos[name] = self.post(service_url, params=params).json()

    def create_group(self, name, description):
        self.get_groups()

        print('creating gitlab/{}...'.format(name), file=sys.stderr)
        service_url = Gitlab.api_url.format(service='groups')

        params = {'name': name, 'path': name, 'description': description,
                  'visibility': 'public'}
        self.groups[name] = self.post(service_url, params=params).json()

    def update_group(self, name, description):
        self.get_groups()

        print('updating gitlab/{}...'.format(name), file=sys.stderr)
        service_url = Gitlab.api_url.format(
            service='groups/{}'.format(name.lower()))

        params = {'name': name, 'path': name, 'description': description,
                  'visibility': 'public'}
        self.groups[name] = self.put(service_url, params=params).json()


if __name__ == '__main__':
    gitlab = Gitlab()

    print('gitlab groups:')
    for k, v in sorted(gitlab.get_groups().items()):
        print(' -', k, v)

    print('gitlab repos:')
    for k, v in sorted(gitlab.get_repos().items()):
        print(' -', k, v)
