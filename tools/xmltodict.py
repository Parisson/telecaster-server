#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Easily import simple XML data to Python dictionary
# http://www.gmta.info/publications/parsing-simple-xml-structure-to-a-python-dictionary

import xml.dom.minidom
import xml.dom.ext
from xml.sax.saxutils import escape


def haschilds(dom):
    # Checks whether an element has any childs
    # containing real tags opposed to just text.
    for childnode in dom.childNodes:
        if childnode.nodeName != "#text" and \
            childnode.nodeName != "#cdata-section":
            return True
    return False


def indexchilds(dom, enc):
    childsdict = dict()
    for childnode in dom.childNodes:
        name = childnode.nodeName.encode(enc)
        if name == "#text" or name == "#cdata-section":
            # ignore whitespaces
            continue
        if haschilds(childnode):
            v = indexchilds(childnode, enc)
        else:
            v = childnode.childNodes[0].nodeValue.encode(enc)
        if name in childsdict:
            if isinstance(childsdict[name], dict):
                # there is multiple instances of this node - convert to list
                childsdict[name] = [childsdict[name]]
            childsdict[name].append(v)
        else:
            childsdict[name] = v
    return childsdict


def xmltodict(data, enc=None):
    dom = xml.dom.minidom.parseString(data.strip())
    return indexchilds(dom, enc)


def dicttoxml(d):

    def unicodify(o):
        if o is None:
            return u'';
        return unicode(o)

    lines = []
    def addDict(node, offset):
        for name, value in node.iteritems():
            if isinstance(value, dict):
                lines.append(offset + u"<%s>" % name)
                addDict(value, offset + u" " * 4)
                lines.append(offset + u"</%s>" % name)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        lines.append(offset + u"<%s>" % name)
                        addDict(item, offset + u" " * 4)
                        lines.append(offset + u"</%s>" % name)
                    else:
                        lines.append(offset + u"<%s>%s</%s>" % (name, escape(unicodify(item)), name))
            else:
                lines.append(offset + u"<%s>%s</%s>" % (name, escape(unicodify(value)), name))

    addDict(d, u"")
    lines.append(u"")
    return u"\n".join(lines)

