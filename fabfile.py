import os
import sys
import shutil
from xml.dom import minidom
from fabric.api import local
from fabric.api import put
from fabric.api import get
from fabric.api import sudo
from fabric.api import prompt
from fabric.api import env
from fabric.utils import abort
from fabric.decorators import hosts
import tidylib

TRUISMS = [
    "y",
    "yes",
    "true",
    "1",
]
# clear the default settings
tidylib.BASE_OPTIONS = {}
env.tidy_options = {
    "add-xml-decl": 1,
    "input-xml": 1,
    "indent": 1,
    "wrap": 0,
}
env.userdata_base = {
    'linux2': os.path.expanduser('~/.boxee/UserData/apps'),
    'darwin': os.path.expanduser(
        '~/Library/Application Support/BOXEE/UserData/apps'),
}
env.platform = sys.platform
env.descriptor_fname = "vimcasts/descriptor.xml"
env.app_name = "vimcasts"
# XXX: Is this cross platform?
env.zip_cmd = "zip -r %s %s -x@exclude.lst"
# external repo settings
env.ext_repo_id = "com.claytron"
env.ext_repo_url = "http://claytron.com/static/boxee"
env.ext_repo_version = "ext_version.txt"
env.ext_repo_host = "zap239.sixfeetup.com"
env.ext_repo_dir = "/usr/local/www/data/boxee"

##########
# Commands
##########


def release_official(ignore="no"):
    print "Preparing release for Boxee blessed repo"
    develop('off')
    _check_status(ignore)
    print "Creating zip archive for the app"
    desc_dom = _descriptor_xml()
    versions = desc_dom.firstChild.getElementsByTagName("version")
    if not versions:
        abort("ERROR: No version number specified")
    version = versions[0].firstChild.data
    archive_name = "%s-%s.zip" % (env.app_name, version)
    # output to the console
    output = local(env.zip_cmd % (archive_name, env.app_name))
    print output


@hosts(env.ext_repo_host)
def release_external(ignore="no"):
    print "Preparing third party repo release"
    develop("off")
    _check_status(ignore)
    # grab the new external app version
    version_file = open(env.ext_repo_version)
    version = version_file.read().strip()
    version_file.close()
    print "Creating zip archive for the app"
    ext_app_id = "%s.%s" % (env.ext_repo_id, env.app_name)
    local("cp -r %s %s" % (env.app_name, ext_app_id))
    _modify_descriptor(ext_app_id, version)
    print "update the index.xml file"
    put("index.xml", ".")
    sudo("mv index.xml %s/." % env.ext_repo_dir)
    local("rm index.xml")
    archive_name = "%s-%s.zip" % (ext_app_id, version)
    local(env.zip_cmd % (archive_name, ext_app_id))
    print "push zip file into 'download' on remote server"
    push_zip_external(archive_name)
    local("rm -rf %s" % ext_app_id)
    local("rm %s" % archive_name)
    # new version number (this is less than optimal)
    version_file = open(env.ext_repo_version, "r")
    version = version_file.read().strip()
    version_file.close()
    major, minor = version.split('.')
    minor = int(minor) + 1
    new_version = "%s.%02d" % (major, minor)
    version_file = open(env.ext_repo_version, 'w')
    version_file.write(new_version)
    version_file.close()


@hosts(env.ext_repo_host)
def push_zip_external(filename=None):
    if filename is None:
        abort("You must specify a file to deploy")
    put(filename, "%s/download/." % env.ext_repo_dir)


def develop(status='on'):
    status = status.lower()

    # Take care of the <test-app> setting in descriptor.xml
    desc_dom = _descriptor_xml()
    xml_file = open(env.descriptor_fname, 'w')
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
    elif status == "on" and not node_list.length:
        test_app = desc_dom.createElement("test-app")
        truth = desc_dom.createTextNode(u"true")
        test_app.appendChild(truth)
        app.appendChild(test_app)
        print msg
        _tidy_up(xml_file, desc_dom)
    # still need to write the file if opened it up
    else:
        _tidy_up(xml_file, desc_dom)
    xml_file.close()

    # Take care of creating a symlink
    if env.platform in env.userdata_base:
        link_location = "%s/%s" % (
            env.userdata_base[env.platform], env.app_name)
        vimcasts_location = os.path.abspath('vimcasts')
        if os.path.lexists(link_location):
            if os.path.islink(link_location):
                if os.readlink(link_location) != vimcasts_location and \
                   status == "on":
                    answer = prompt("Remove symlink %s?" % link_location)
                    if answer in TRUISMS:
                        os.unlink(link_location)
                        print "Symlink %s removed" % link_location
                        develop('on')
                elif status == "off":
                    print "Removing symlink from %s" % link_location
                    os.unlink(link_location)
            else:
                answer = prompt("Remove %s?" % link_location)
                if answer.lower() in TRUISMS:
                    shutil.rmtree(link_location)
                    print "%s removed" % link_location
                    develop('on')
        elif status == "on":
            print "Symlinking %s" % link_location
            os.symlink(vimcasts_location, link_location)
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


def _descriptor_xml(descriptor=env.descriptor_fname):
    if os.path.exists(descriptor):
        desc_dom = minidom.parse(descriptor)
        return desc_dom
    else:
        abort("File not found: %s" % descriptor)


def _tidy_up(xml_file, dom_node):
    document, errors = tidylib.tidy_document(
        dom_node.toxml(), env.tidy_options)
    xml_file.write(document)


@hosts(env.ext_repo_host)
def _modify_descriptor(ext_app_id, version):
    print "create third party descriptor xml"
    desc_dom = _descriptor_xml("%s/descriptor.xml" % ext_app_id)
    xml_file = open("%s/descriptor.xml" % ext_app_id, 'w')
    app = desc_dom.firstChild
    # Add a repo id node
    repo_id_node = desc_dom.createElement("repository-id")
    repo_id = desc_dom.createTextNode(env.ext_repo_id)
    repo_id_node.appendChild(repo_id)
    app.appendChild(repo_id_node)
    # Change the repo url
    url_nodes = app.getElementsByTagName("repository")
    repo_url_node = url_nodes.item(0)
    repo_url_node.firstChild.replaceWholeText(env.ext_repo_url)
    # change version
    version_node = app.getElementsByTagName("version").item(0)
    version_node.firstChild.replaceWholeText(version)
    # change app id
    id_node = app.getElementsByTagName("id").item(0)
    id_node.firstChild.replaceWholeText(ext_app_id)
    # write out changes
    _tidy_up(xml_file, desc_dom)
    # modify the existing index.xml and add our new app
    get("%s/index.xml" % env.ext_repo_dir, ".")
    ext_desc_dom = _descriptor_xml("index.xml")
    ext_app_node = ext_desc_dom.firstChild
    ext_apps = ext_desc_dom.getElementsByTagName("app")
    orig_app_node = None
    # find our app
    for ext_app in ext_apps:
        app_id = ext_app.getElementsByTagName("id")[0].firstChild.data
        if app_id == ext_app_id:
            orig_app_node = ext_app
    # remove app from current xml file
    if orig_app_node is not None:
        ext_app_node.removeChild(orig_app_node)
    ext_app_node.appendChild(app)
    # write out index.xml
    index_file = open("index.xml", "w")
    _tidy_up(index_file, ext_desc_dom)
    index_file.close()
