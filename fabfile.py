import os
import sys
from xml.dom import minidom
from fabric.api import local
from fabric.api import put
from fabric.utils import abort
from fabric.decorators import hosts
import tidylib

# clear the default settings
tidylib.BASE_OPTIONS = {}

TIDY_OPTIONS = {
    "add-xml-decl": 1,
    "input-xml": 1,
    "indent": 1,
    "wrap": 0,
}
USERDATA_BASE = {
    # XXX: need to test on linux
    'linux': os.path.expanduser('~/.boxee/UserData/apps'),
    'darwin': os.path.expanduser(
        '~/Library/Application Support/BOXEE/UserData/apps'),
}
PLATFORM = sys.platform
DESCRIPTOR_FNAME = "vimcasts/descriptor.xml"
APP_NAME = "vimcasts"
# XXX: Is the cross platform?
ZIP_CMD = "zip -r %s %s -x@exclude.lst"
# external repo settings
EXT_REPO_ID = "com.claytron"
EXT_REPO_URL = "http://claytron.com/static/boxee"
EXT_REPO_VERSION = "ext_version.txt"
EXT_REPO_HOST = "zap239.sixfeetup.com"
EXT_REPO_DIR = "/usr/local/www/data/boxee"

##########
# Commands
##########


def release_official(ignore="no"):
    print "Preparing release for Boxee blessed repo"
    _check_status(ignore)
    develop('off')
    print "Creating zip archive for the app"
    desc_dom = _descriptor_xml()
    versions = desc_dom.firstChild.getElementsByTagName("version")
    if not versions:
        abort("ERROR: No version number specified")
    version = versions[0].firstChild.data
    archive_name = "%s-%s.zip" % (APP_NAME, version)
    # output to the console
    local(ZIP_CMD % (archive_name, APP_NAME))


@hosts(EXT_REPO_HOST)
def release_external(ignore="no"):
    print "Preparing third party repo release"
    develop("off")
    _check_status(ignore)
    version = "x.x"
    print "Creating zip archive for the app"
    ext_app_id = "%s.%s" % (EXT_REPO_ID, APP_NAME)
    local("cp -r %s %s" % (APP_NAME, ext_app_id))
    print "create third party descriptor xml"
    desc_dom = _descriptor_xml("%s/descriptor.xml" % ext_app_id)
    # remove/add repo id
    # remove/add repo url
    # change version
    # create new dom with apps/app
    # write out index.xml
    print "update the index.xml file"
    put("index.xml", EXT_REPO_DIR)
    local("rm index.xml")
    archive_name = "%s-%s.zip" % (ext_app_id, version)
    local(ZIP_CMD % (archive_name, APP_NAME))
    print "push zip file into 'download' on remote server"
    push_zip_external(archive_name)
    local("rm -rf %s" % ext_app_id)


@hosts(EXT_REPO_HOST)
def push_zip_external(filename=None):
    if filename is None:
        abort("You must specify a file to deploy")
    put(filename, "%s/download/." % EXT_REPO_DIR)


def develop(status='on'):
    status = status.lower()

    # Take care of the <test-app> setting in descriptor.xml
    desc_dom = _descriptor_xml()
    with open(DESCRIPTOR_FNAME, 'w') as xml_file:
        msg = "Turning %s <test-app> in descriptor.xml" % status
        app = desc_dom.firstChild
        node_list = app.getElementsByTagName("test-app")
        if node_list.length:
            if status == "off":
                print msg
                app.removeChild(node_list.item(0))
                _tidy_up(xml_file, desc_dom)
            else:
                test_app = node_list.item(0)
                test_app.firstChild.replaceWholeText(u"true")
                print msg
                _tidy_up(xml_file, desc_dom)
        else:
            test_app = desc_dom.createElement("test-app")
            truth = desc_dom.createTextNode(u"true")
            test_app.appendChild(truth)
            app.appendChild(test_app)
            print msg
            _tidy_up(xml_file, desc_dom)

    # Take care of creating a symlink
    if PLATFORM in USERDATA_BASE:
        link_location = "%s/%s" % (USERDATA_BASE[PLATFORM], APP_NAME)
        if os.path.lexists(link_location):
            if os.path.islink(link_location):
                if status == "on":
                    msg = "WARNING: Symlink to %s already exists"
                    print msg % link_location
                    # TODO: check if it is the same, ask to remove it?
                    #os.unlink(link_location)
                elif status == "off":
                    print "Removing symlink from %s" % link_location
                    os.unlink(link_location)
            else:
                # TODO: handle this case properly
                print "Can't create or remove symlink"
        elif status == "on":
            print "Symlinking %s" % link_location
            os.symlink(os.path.abspath('vimcasts'), link_location)
    else:
        print "WARNING: Cannot create symlink on this platform"


################
# Helper Methods
################


def _check_status(ignore):
    output = local("git status -s")
    msg = "There are local changes, commit or revert before continuing"
    if output and ignore != "ignore":
        abort(msg)


def _descriptor_xml(descriptor=DESCRIPTOR_FNAME):
    if os.path.exists(descriptor):
        desc_dom = minidom.parse(descriptor)
        return desc_dom
    else:
        abort("File not found: %s" % descriptor)


def _tidy_up(xml_file, dom_node):
    document, errors = tidylib.tidy_document(dom_node.toxml(), TIDY_OPTIONS)
    xml_file.write(document)
