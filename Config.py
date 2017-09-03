from collections import OrderedDict
from uuid import uuid1


def get_perspective(name):
    perspective = OrderedDict()

    perspective['name'] = name

    sig_cnv = OrderedDict()
    perspective['signalCanvases'] = sig_cnv

    sig_cnv['order'] = ['OSCI', 'SPEC']
    sig_cnv['assign'] = []
    sig_cnv['contourLims'] = []

    lev_cnv = OrderedDict()
    perspective['levelCanvases'] = lev_cnv

    lev_cnv['order'] = ['Word', 'Phoneme']

    twodim_cnv = OrderedDict()
    perspective['twoDimCanvases'] = twodim_cnv

    twodim_cnv['order'] = []

    return perspective


def get_default_emu_config():
    config = OrderedDict()

    perspectives = []
    config['perspectives'] = perspectives

    perspectives.append(get_perspective('default'))

    restrictions = OrderedDict()
    config['restrictions'] = restrictions

    restrictions['showPerspectivesSidebar'] = True

    buttons = OrderedDict()
    config['activeButtons'] = buttons

    buttons['saveBundle'] = True
    buttons['showHierarchy'] = False

    return config


def getLevel(name, labelname, itemtype='SEGMENT', labeltype='STRING'):
    level = OrderedDict()

    level['name'] = name
    level['type'] = itemtype

    attrs = []
    level['attributeDefinitions'] = attrs

    if not type(labelname) is list:
        labelname = [labelname]

    for label in labelname:
        attr = OrderedDict()
        attrs.append(attr)

        attr['name'] = label
        attr['type'] = labeltype

    return level


def getLink(from_level, to_level, type='ONE_TO_MANY'):
    link = OrderedDict()
    link['type'] = type
    link['superlevelName'] = from_level
    link['sublevelName'] = to_level
    return link


def get_config(name):
    config = OrderedDict()

    config['name'] = name
    config['UUID'] = str(uuid1())
    config['mediafileExtension'] = 'wav'

    tracks = []
    config['ssffTrackDefinitions'] = tracks

    levels = []
    config['levelDefinitions'] = levels

    levels.append(getLevel('Utterance', 'Utterance', itemtype='ITEM'))
    levels.append(getLevel('Word', 'Word'))
    levels.append(getLevel('Phoneme', ['Phoneme', 'SAMPA', 'IPA']))

    links = []
    config['linkDefinitions'] = links

    links.append(getLink('Utterance', 'Word'))
    links.append(getLink('Word', 'Phoneme'))

    config['EMUwebAppConfig'] = get_default_emu_config()

    return config
