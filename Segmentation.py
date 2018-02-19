#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
from collections import OrderedDict

pl_sampa_map = {'ni': "n'", 'si': "s'", 'tsi': "ts'", 'zi': "z'", 'dzi': "dz'", 'en': 'e~', 'on': 'o~'}
pl_ipa_map = {'e': 'ɛ', 'en': 'ɛ̃', 'I': 'ɨ', 'o': 'ɔ', 'on': 'ɔ̃', 'si': 'ɕ', 'dz': 'dz', 'dzi': 'dʑ',
              'dZ': 'dʐ', 'g': 'ɡ', 'ni': 'ɲ', 'S': 'ʂ', 'tsi': 'tɕ', 'ts': 'ts', 'tS': 'tʂ', 'zi': 'ʑ',
              'Z': 'ʐ'}

EPSILON = 0.01
besi = re.compile('^.*_[BESI]$')


class Segment:
    def __init__(self, start, len, text, idgen):
        assert start >= 0 and len >= 0, 'start or len smaller than 0 for ' + text

        self.start = start
        self.len = len
        self.end = round(self.start + self.len, 2)
        self.text = text
        self.id = next(idgen)

    def wraps(self, other):
        return other.start - self.start > -EPSILON and other.end - self.end < EPSILON


class Level:
    def __init__(self, idgen):
        self.segments = []
        self.idgen = idgen

    def add(self, start, len, text):
        self.segments.append(Segment(start, len, text, self.idgen))

    def sort(self):
        self.segments = sorted(self.segments, key=lambda seg: seg.start)

    def fillGaps(self):
        self.sort()
        gaps = []
        for prev, next in zip(self.segments, self.segments[1:]):
            if next.start > prev.end:
                gaps.append(Segment(prev.end, next.start - prev.end, '', self.idgen))
            if next.start < prev.end:
                prev.end = next.start
                prev.len = prev.end - prev.start
        self.segments.extend(gaps)
        self.sort()

    def getAnnotation(self, name, labelname, samplerate=16000, get_segments=True, ph_labels=None):

        level = OrderedDict()

        level['name'] = name
        if get_segments:
            level['type'] = 'SEGMENT'
        else:
            level['type'] = 'ITEM'

        items = []
        level['items'] = items

        for seg in self.segments:
            item = OrderedDict()
            items.append(item)

            item['id'] = seg.id

            if get_segments:
                item['sampleStart'] = int(samplerate * seg.start)
                item['sampleDur'] = int(samplerate * seg.len)

            labels = []
            item['labels'] = labels

            label = OrderedDict()
            labels.append(label)

            label['name'] = labelname

            label['value'] = seg.text

            if ph_labels:
                for scriptame, map in ph_labels:
                    label = OrderedDict()
                    labels.append(label)
                    label['name'] = scriptame
                    if seg.text in map:
                        label['value'] = map[seg.text]
                    else:
                        label['value'] = seg.text

        return level

    def getLinks(self, other_ctm):
        links = []

        for seg in self.segments:
            for other_seg in other_ctm.segments:
                if seg.wraps(other_seg):
                    link = OrderedDict()
                    links.append(link)
                    link['fromID'] = seg.id
                    link['toID'] = other_seg.id

        return links


class IDgen:
    def __init__(self):
        self.id_cnt = 0

    def __next__(self):
        self.id_cnt += 1
        return self.id_cnt


class Segmentation:
    def __init__(self):
        self.idgen = IDgen()
        self.words = Level(self.idgen)
        self.phonemes = Level(self.idgen)

    def read(self, file, rm_besi=True, script=None):
        with codecs.open(file, encoding='utf-8', mode='r') as f:
            for l in f:
                tok = l.strip().split(' ')
                assert len(tok) == 5, 'Wrong tok count in file {}: {}'.format(file, l)
                if tok[0][0] == '@':
                    ph = tok[4]

                    if rm_besi:
                        if besi.match(ph):
                            ph = ph[:-2]
                    if script == 'sampa':
                        if ph in pl_sampa_map:
                            ph = pl_sampa_map[ph]
                    elif script == 'ipa':
                        if ph in pl_ipa_map:
                            ph = pl_ipa_map[ph]

                    self.phonemes.add(round(float(tok[2]), 2), round(float(tok[3]), 2), ph)
                else:
                    self.words.add(round(float(tok[2]), 2), round(float(tok[3]), 2), tok[4])

        self.words.fillGaps()
        self.phonemes.fillGaps()

    def getUttLevel(self, name):
        level = Level(self.idgen)
        min = max = 0
        for seg in self.words.segments:
            if min > seg.start:
                min = seg.start
            if max < seg.end:
                max = seg.end
        level.add(min, max, name)
        return level


def segmentation_to_emu_annot(file, name, samplerate=16000.0, rm_besi=True, script=None):
    seg = Segmentation()
    seg.read(file, rm_besi=rm_besi, script=script)

    annot = OrderedDict()

    annot['name'] = name
    annot['annotates'] = name + '.wav'
    annot['sampleRate'] = samplerate

    levels = []
    annot['levels'] = levels

    utterance = seg.getUttLevel(name)
    words = seg.words
    phonemes = seg.phonemes

    levels.append(utterance.getAnnotation('Utterance', 'Utterance', get_segments=False))

    levels.append(words.getAnnotation('Word', 'Word', samplerate))

    levels.append(phonemes.getAnnotation('Phoneme', 'Phoneme', samplerate,
                                         ph_labels=[('SAMPA', pl_sampa_map), ('IPA', pl_ipa_map)]))

    uttlinks = utterance.getLinks(words)
    wordlinks = words.getLinks(phonemes)

    annot['links'] = uttlinks + wordlinks

    return annot


def annot_to_ctm(annot, samplerate=16000.0, name='input'):
    word_level = None
    phone_level = None
    for level in annot['levels']:
        if level['name'] == 'Word':
            word_level = level
        elif level['name'] == 'Phoneme':
            phone_level = level

    if not word_level or not phone_level:
        raise RuntimeError('Word or phoneme level missing!')

    seg = Segmentation()
    for word in word_level['items']:
        start = word['sampleStart'] / samplerate
        dur = word['sampleDur'] / samplerate
        text = word['labels'][0]['value']
        seg.words.add(start, dur, text)
    for phone in phone_level['items']:
        start = phone['sampleStart'] / samplerate
        dur = phone['sampleDur'] / samplerate
        text = phone['labels'][0]['value']
        seg.phonemes.add(start, dur, text)

    ret = []
    ph = 0
    for word in seg.words.segments:
        while ph < len(seg.phonemes.segments):
            phone = seg.phonemes.segments[ph]
            if phone.end <= word.start:
                ret.append('@{} 1 {} {} {}\n'.format(name, phone.start, phone.len, phone.text))
                ph += 1
            else:
                break
        ret.append('{} 1 {} {} {}\n'.format(name, word.start, word.len, word.text))
    while ph < len(seg.phonemes.segments):
        phone = seg.phonemes.segments[ph]
        ret.append('@{} 1 {} {} {}\n'.format(name, phone.start, phone.len, phone.text))
        ph += 1

    return ''.join(ret)
