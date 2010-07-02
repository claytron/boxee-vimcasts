import os
import sys
from xml.dom import minidom
from fabric.utils import abort
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
    'linux': os.path.expanduser('~/.boxee/UserData/apps'),
    'darwin': os.path.expanduser(
        '~/Library/Application Support/BOXEE/UserData/apps'),
}
PLATFORM = sys.platform
DESCRIPTOR_FNAME = "vimcasts/descriptor.xml"
APP_NAME = "vimcasts"


def release():
    print "boxee release"
    print "test for local changes and abort if there are some (git)"
    print "test for <test-app> setting"
    print "create zip ignoring hidden files, etc."


def release_claytron():
    print "claytron release"
    print "bump version"
    print "create third party descriptor xml"
    print "push zip file into 'download' on remote server"
    print "update the index.xml file"


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


def _descriptor_xml():
    if os.path.exists(DESCRIPTOR_FNAME):
        desc_dom = minidom.parse(DESCRIPTOR_FNAME)
        return desc_dom
    else:
        abort("File not found: %s" % DESCRIPTOR_FNAME)


def _tidy_up(xml_file, dom_node):
    document, errors = tidylib.tidy_document(dom_node.toxml(), TIDY_OPTIONS)
    xml_file.write(document)
