import sys

from .oauth2 import OAuth2Service
from .config import config


class Bitbucket(OAuth2Service):
    client = config['bitbucket']['client']
    secret = config['bitbucket']['secret']
    redir_url = 'http://127.0.0.1:8080'
    autho_url = 'https://bitbucket.org/site/oauth2/authorize'
    token_url = 'https://bitbucket.org/site/oauth2/access_token'
    api_url = 'https://api.bitbucket.org/2.0/{service}'
    token_file = '.bitbucket-auth'
    scope = None

    def __init__(self):
        super(Bitbucket, self).__init__(Bitbucket)
        self.groups = None
        self.repos = None

    def reponame(self, project):
        return project['full_name']

    def groupname(self, group):
        return group['username']

    def get_repos(self, force=False):
        if self.repos and not force:
            return self.repos

        print('listing bitbucket repositories...', file=sys.stderr)
        service_url = Bitbucket.api_url.format(service='repositories')

        params = {'role': 'member'}
        projects = self.get(service_url, params=params).json()
        next_projects = projects
        while 'next' in next_projects:
            next_projects = self.get(next_projects['next']).json()
            projects['values'] += next_projects['values']

        self.repos = dict([(self.reponame(p), p) for p in projects['values']])
        return self.repos

    def get_groups(self, force=False):
        if self.groups and not force:
            return self.groups

        print('listing bitbucket groups...', file=sys.stderr)
        service_url = Bitbucket.api_url.format(service='teams')

        params = {'role': 'member'}
        teams = self.get(service_url, params=params).json()
        next_teams = teams
        while 'next' in next_teams:
            next_teams = self.get(next_teams['next']).json()
            teams['values'] += next_teams['values']

        self.groups = dict([(self.groupname(t), t) for t in teams['values']])

        service_url = Bitbucket.api_url.format(service='user')
        user = self.get(service_url).json()
        self.groups[self.groupname(user)] = user

        return self.groups

    def create_repo(self, reponame, **kwargs):
        self.get_repos()

        print('creating bitbucket/{}...'.format(reponame), file=sys.stderr)
        service_url = Bitbucket.api_url.format(
            service='repositories/{}'.format(reponame.lower()))

        [group, name] = reponame.split('/', 1)
        params = {
            'name': name,
            'description': kwargs.get('description', ''),
            'scm': 'git',
            'is_private': str(kwargs.get('private', False)).lower(),
            'owner': group,
        }

        language = kwargs.get('language', '').lower()
        if language not in ['html', 'cmake', 'makefile']:
            params['language'] = language

        self.repos[reponame] = self.post(service_url, json=params).json()

    def delete_repo(self, reponame):
        self.get_repos()

        print('deleting bitbucket/{}...'.format(reponame), file=sys.stderr)
        service_url = Bitbucket.api_url.format(
            service='repositories/{}'.format(reponame.lower()))

        self.delete(service_url)
        del(self.repos[reponame])


if __name__ == '__main__':
    bitbucket = Bitbucket()

    print('bitbucket groups:')
    for k, v in sorted(bitbucket.get_groups().items()):
        print(' -', k, v)

    print('bitbucket repos:')
    for k, v in sorted(bitbucket.get_repos().items()):
        print(' -', k, v)
