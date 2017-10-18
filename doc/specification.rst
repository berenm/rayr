Specification
=============

The goal of rayr is to have various *sources* (local folders) synchronized with *destinations* - or remotes (public or private repositories hosting servers).
When we talk about synchronization, it is a stateless sync, ala rsync or rclone. The tool has no memory of what the previous synchronization did.
However, it will do its best to put both ends at the same state, repository wise.

As such, we can base some of the way to interact with rayr as with rsync or rclone.

Repositories format
-------------------

For now, rayr only deals with git repositories. It should be fairly easy, and desirable, to add mercurial to the list. Other SCMs could be added, provided they have a similar push/pull paradigm and some online servers supports them.

Providers
---------

The following providers will be supported
 * Github
 * Gitlab
 * Bitbucket
 * Gogs and Gitea

We possibly could support Rhodecode in the community edition variation.

Configuration format
--------------------

[This is a proposal and not the current way of configuration]
Configuration should done in a format that is human readable, such as json, yaml, or config file format.
Configuration should also be doable with the tool itself, upon invoking ``rayr config``

We should display current remotes and a way to add, modify and delete a remote.

Remotes have short names that allow the user to remember them. In a classic scenario, we can provide reasonable defaults (such as ``github``, ``gitlab`` and so on).

Authentication
--------------

Most providers provide two ways to authenticate. With OAuth or with application password. As **rayr** is open source, it cannot embed its own set of credentials.
Therefore, the user must provide them. Alternatively, we can ask the user to provide an application password for the providers that supports them.

Synchronization
---------------

We can synchronize with the following command:

.. code:: bash

    rayr sync <localfolder> <remotename>
    rayr sync <remotename> <localfolder>


Options
-------

We should support classic options: log location, verbosity, config file location override.