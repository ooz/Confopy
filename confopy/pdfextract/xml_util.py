# coding: utf-8

from xml.dom import Node
import xml.sax.saxutils as SU

def getChildElementsByTagName(node, tagName):
    children = node.childNodes
    elems = list()
    for i in range(children.length):
        child = children.item(i)
        if child.nodeType == Node.ELEMENT_NODE and child.nodeName == tagName:
            elems.append(child)
    return elems

def escape(string):
    return (SU.escape(string)).replace(u"\"", u"&quot;")

