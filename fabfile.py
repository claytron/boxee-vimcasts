import os
import sys
from xml.dom import minidom

USERDATA_BASE = {
    'linux': os.path.expanduser('~/.boxee/UserData'),
    'osx': os.path.expanduser('~/Library/Application Support/BOXEE/UserData')
}


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


def develop():
    print "Turning on <test-app> in descriptor.xml"
    desc_dom = _descriptor_xml()
    with open('descriptor.xml', 'w') as desc_xml:
        app = desc_dom.firstChild
        node_list = app.getElementsByTagName("test-app")
        if node_list.length:
            test_app = node_list.item(0)
            test_app.firstChild.replaceWholeText(u"true")
            desc_dom.writexml(desc_xml)
        else:
            test_app = desc_dom.createElement("test-app")
            truth = desc_dom.createTextNode(u"true")
            test_app.appendChild(truth)
            app.appendChild(test_app)
            desc_dom.writexml(desc_xml)
    # TODO
    print "test for platform and place symlink into UserData/apps dir"


def _descriptor_xml():
    if os.path.exists("descriptor.xml"):
        desc_dom = minidom.parse("descriptor.xml")
        return desc_dom
    else:
        sys.exit(1)
