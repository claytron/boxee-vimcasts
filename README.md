# Description

![Vimcasts Logo](http://github.com/claytron/boxee-vimcasts/raw/master/thumb.png)

This is a Boxee app that shows episodes from [vimcasts.org](http://vimcasts.org). Report any issues in the [issue tracker](http://github.com/claytron/boxee-vimcasts/issues).

# Development and Deployment

## Requirements and installation

- Python 2.6
- Fabric
- PyTidyLib

Create a virtualenv named `fabric` to run the commands

    $ sudo easy_install virtualenv
    $ mkdir ~/.virtualenvs
    $ cd ~/.virtualenvs
    $ virtualenv --python=python2.6 --no-site-packages fabric

Activate the virtualenv

    $ cd fabric
    $ source bin/activate

Install the libraries needed

    (fabric)$ easy_install Fabric
    (fabric)$ easy_install PyTidyLib

Now you can use the commands below

## Commands

Go to the root of the git clone

    (fabric)$ cd path/to/boxee-vimcasts

### Development mode

Turn on "development" mode

    (fabric)$ fab develop

Turn off "development" mode

    (fabric)$ fab develop:off


### External Repo Release

Deploy to the third party repo

    (fabric)$ fab release_external

Deploy to the third party repo ignoring any working copy changes

    (fabric)$ fab release_external:ignore

### Official Release Preparation

Prepare release tarball for Boxee blessed repo

    (fabric)$ fab release_offical

Prepare release tarball for Boxee blessed repo ignoring any working copy changes

    (fabric)$ fab release_official:ignore
