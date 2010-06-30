import os
import sys
from xml.dom import minidom
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
        '~/Library/Application Support/BOXEE/UserData/apps')
}
PLATFORM = sys.platform
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
    desc_dom = _descriptor_xml()
    with open('descriptor.xml', 'w') as xml_file:
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
    # TODO: handle removal of symlink when status='off'
    if PLATFORM in USERDATA_BASE:
        link_location = "%s/%s" % (USERDATA_BASE[PLATFORM], APP_NAME)
        if os.path.lexists(link_location):
            # TODO: check if it is the same, ask to remove it?
            print "WARNING: Symlink to %s already exists" % link_location
            #os.unlink(link_location)
        elif os.path.exists(link_location):
            # TODO: ask to remove it?
            print "WARNING: Something is in the way %s" % link_location
            #shutil.rmtree(link_location)
        else:
            print "Symlinking %s" % link_location
            os.symlink(os.path.abspath('.'), link_location)
    else:
        print "WARNING: Cannot create symlink on this platform"


def _descriptor_xml():
    if os.path.exists("descriptor.xml"):
        desc_dom = minidom.parse("descriptor.xml")
        return desc_dom
    else:
        sys.exit(1)

def _tidy_up(xml_file, dom_node):
    document, errors = tidylib.tidy_document(dom_node.toxml(), TIDY_OPTIONS)
    xml_file.write(document)
