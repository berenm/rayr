Replicate All Your (Git) Repositories
================================================================================

Python script to help you replicate your git repositories across multiple
hosting services, such as github, gitlab or bitbucket (for now).

Repositories and groups are created automatically from a given reference (one
of the hosting service), on the others using the API and local mirrors are
created to synchronize the commits between the remotes.

One of the remote will act as the master and the other will be mirrored,
any commit that has not been pushed to the master will be pruned.

Currently only public repositories are replicated.

CONFIGURATION
--------------------------------------------------------------------------------

The script requires OAuth2 application tokens for every hosting service, and
will look for them in a ``.rayrrc`` JSON configuration file located in the
current directory.

You will need to register your own (maybe private) applications on each of the
hosting service to use the script and fill the configuration file with the
corresponding tokens.

The configuration should have the following structure:

.. code:: json

    {
        "gitlab": {
            "client": "<client token>",
            "secret": "<secret token>",
            "enabled": true,
            "private": false
        },
        "github": {
            "client": "<client token>",
            "secret": "<secret token>",
            "enabled": true,
            "private": false
        },
        "bitbucket": {
            "client": "<client token>",
            "secret": "<secret token>",
            "enabled": true,
            "private": false
        },
        "exclude": {
            "groups": ["group1"],
            "repos": ["group/repo"]
        }
    }

OAuth2 authentication tokens and local mirrors will all be saved relative to
the current directory.

LICENSE
-------------------------------------------------------------------------------

 This is free and unencumbered software released into the public domain.

 See accompanying file UNLICENSE or copy at http://unlicense.org/UNLICENSE
