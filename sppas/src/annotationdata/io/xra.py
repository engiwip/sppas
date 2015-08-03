#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------

from datetime import datetime
import xml.etree.cElementTree as ET

from annotationdata.transcription       import Transcription
from annotationdata.hierarchy           import Hierarchy
from annotationdata.media               import Media
from annotationdata.annotation          import Annotation
from annotationdata.label.label         import Label
from annotationdata.label.text          import Text
from annotationdata.ptime.location      import Location
from annotationdata.ptime.localization  import Localization
from annotationdata.ptime.point         import TimePoint
from annotationdata.ptime.interval      import TimeInterval
from annotationdata.ptime.disjoint      import TimeDisjoint
from annotationdata.ptime.framepoint    import FramePoint
from annotationdata.ptime.frameinterval import FrameInterval
from annotationdata.ptime.framedisjoint import FrameDisjoint

from utils import indent
from utils import gen_id

# ---------------------------------------------------------------------------

class XRA(Transcription):
    """
    xra files are the native file format of the GPL tool SPPAS.
    """

    __format = '1.2'

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Initialize a new XRA instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)

    # -----------------------------------------------------------------

    @staticmethod
    def detect(filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        return root.find('Tier') is not None

    # -----------------------------------------------------------------

    def read(self, filename):
        """
        Import a transcription from a .xra file.
        @type filename: str
        @param filename: filename
        """
        tree = ET.parse(filename)
        root = tree.getroot()

        self.__id_tier_map = {}

        metadataRoot = root.find('Metadata')
        if metadataRoot is not None:
            XRA.__read_metadata(self, metadataRoot)

        for tierRoot in root.findall('Tier'):
            self.__read_tier(tierRoot)

        for mediaRoot in root.findall('Media'):
            self.__read_media(mediaRoot)

        hierarchyRoot = root.find('Hierarchy')
        if hierarchyRoot is not None:
            self.__read_hierarchy(hierarchyRoot)

        for vocabularyRoot in root.findall('Vocabulary'):
            self.__read_vocabulary(vocabularyRoot)

    # End read
    # -----------------------------------------------------------------

    def __read_media(self, mediaRoot):
        # Create a Media instance
        mediaid   = mediaRoot.attrib['id']
        mediaurl  = mediaRoot.attrib['url']
        mediamime = ''
        if 'mimetype' in mediaRoot.attrib:
            mediamime = mediaRoot.attrib['mimetype']

        media = Media( mediaid,mediaurl,mediamime )

        # Add content if any
        contentRoot = mediaRoot.find('Content')
        if contentRoot:
            media.content = contentRoot.text

        # link to tiers
        for tierNode in mediaRoot.findall('Tier'):
            tier = self.__id_tier_map[tierNode.attrib['id']]
            tier.SetMedia( media )

    # -----------------------------------------------------------------

    def __read_hierarchy(self, hierarchyRoot):
        for linkNode in hierarchyRoot.findall('Link'):
            try:
                htype = linkNode.attrib['type']
                formerID = linkNode.attrib['from']
                latterID = linkNode.attrib['to']
            except Exception:
                # XRA < 1.2
                htype = linkNode.attrib['Type']
                formerID = linkNode.attrib['From']
                latterID = linkNode.attrib['To']

            former = self.__id_tier_map[formerID]
            latter = self.__id_tier_map[latterID]

            self._hierarchy.addLink(htype, former, latter)

    # -----------------------------------------------------------------

    def __read_vocabulary(self, vocabularyRoot):
        vocab = {}
        for entryNode in vocabularyRoot.findall('Entry'):
            t = Text(entryNode.text)
            vocab[t] = None
            # TODO: add descriptions

        for tierNode in vocabularyRoot.findall('Tier'):
            try:
                idtier = tierNode.attrib['id']
            except Exception:
                # XRA < 1.2
                idtier = tierNode.attrib['ID']
            tier = self.__id_tier_map[idtier]
            tier.ctrlvocab = vocab

    # -----------------------------------------------------------------

    def __read_tier(self, tierRoot):
        name = tierRoot.attrib['tiername']
        tier = self.NewTier(name)

        try:
            tid = tierRoot.attrib['id']
        except Exception:
            # XRA < 1.2
            tid = tierRoot.attrib['ID']
        self.__id_tier_map[tid] = tier

        metadataRoot = tierRoot.find('Metadata')
        if metadataRoot is not None:
            XRA.__read_metadata(tier, metadataRoot)

        # TODO: read medias somehow

        for annotationRoot in tierRoot.findall('Annotation'):
            XRA.__read_annotation(tier, annotationRoot)

    # -----------------------------------------------------------------

    @staticmethod
    def __read_annotation(tier, annotationRoot):

        locationRoot = annotationRoot.find('Location')
        location = XRA.__parse_location(locationRoot)

        labelRoot = annotationRoot.find('Label')
        label = XRA.__parse_label(labelRoot)

        annotation = Annotation(location, label)
        tier.Add(annotation)

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_location(locationRoot):
        localizationList = []
        for localizationRoot in locationRoot.findall('Localization'):
            localization = XRA.__parse_localization(localizationRoot)

            localizationList.append(localization)

        location = Location(localizationList[0])
        for localization in localizationList[1:]:
            location.AddValue(localization)

        return location

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_localization(localizationRoot):

        underlyingNode = localizationRoot.find('*')
        locstr = underlyingNode.tag.lower()

        if locstr == 'timepoint':
            point = XRA.__parse_time_point(underlyingNode)
            localization = Localization(point)

        elif locstr == 'framepoint':
            point = XRA.__parse_frame_point(underlyingNode)
            localization = Localization(point)

        elif locstr in ['timeinterval', 'frameinterval' ]:
            interval = XRA.__parse_interval(underlyingNode)
            localization = Localization(interval)

        elif locstr in [ 'timedisjoint', 'framedisjoint' ]:
            disjoint = XRA.__parse_disjoint(underlyingNode)
            localization = Localization(disjoint)

        else:
            raise Exception(
                "Localization is not a valid type: %s" %
                repr(underlyingNode.tag))

        score = float(localizationRoot.attrib['score'])
        localization.SetScore(score)

        return localization

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_time_point(timePointNode):
        midpoint = float(timePointNode.attrib['midpoint'])
        radius = float(timePointNode.attrib['radius'])

        return TimePoint(midpoint, radius)

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_frame_point(framePointNode):
        midpoint = int(framePointNode.attrib['midpoint'])
        radius   = int(framePointNode.attrib['radius'])

        return FramePoint(midpoint, radius)

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_interval(intervalRoot):
        isTimeInterval = intervalRoot.tag.lower() == 'timeinterval'

        beginNode = intervalRoot.find('Begin')
        begin = (XRA.__parse_time_point(beginNode) if
                 isTimeInterval else
                 XRA.__parse_frame_point(beginNode))

        endNode = intervalRoot.find('End')
        end = (XRA.__parse_time_point(endNode) if
               isTimeInterval else
               XRA.__parse_frame_point(endNode))

        return (TimeInterval(begin, end) if
                isTimeInterval else
                FrameInterval(begin, end))

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_disjoint(disjointRoot):
        isTimeDisjoint = disjointRoot.tag.lower() == 'timedisjoint'
        intervalList = []

        for intervalRoot in (
            disjointRoot.findall('TimeInterval' if
                                 isTimeDisjoint else
                                 'FrameInterval')
        ):
            interval = XRA.__parse_interval(intervalRoot)
            intervalList.append(interval)

        return (TimeDisjoint(*intervalList) if
                isTimeDisjoint else
                FrameDisjoint(*intervalList))

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_label(labelRoot):
        label = Label()

        if 'scoremode' in labelRoot.attrib:
            # FIXME: it's min or max usually,
            # but there's no reason for it to only be builtins
            fun = globals()['__builtins__'][labelRoot.attrib['scoremode']]
            label.SetFunctionScore(fun)

        for textNode in labelRoot.findall('Text'):
            score = float(textNode.attrib['score'])
            content = (textNode.text if
                       textNode.text is not None else '')

            if 'type' in textNode.attrib:
                text = Text(content, score, textNode.attrib['type'])
            else:
                text = Text(content, score)

            label.AddValue(text)

        return label

    # -----------------------------------------------------------------

    @staticmethod
    def __read_metadata(metaObject, metadataRoot):
        for entryNode in metadataRoot.findall('Entry'):
            try:
                key = entryNode.attrib['Key'].lower()
            except Exception:
                # XRA 1.1
                key = entryNode.attrib['key'].lower()
            value = entryNode.text
            metaObject.metadata[key] = value

    # -----------------------------------------------------------------

    def write(self, filename, encoding='UTF-8'):
        """
        Write a XRA file.
        """
        try:
            root = ET.Element('Document')
            root.set('Author', 'SPPAS')
            root.set('Date', datetime.now().strftime("%Y-%m-%d"))
            root.set('Format', XRA.__format)

            self.__tier_id_map = {}
            self.__tier_counter = 0

            metadataRoot = ET.SubElement(root, 'Metadata')
            XRA.__format_metadata(metadataRoot, self)
            if len(metadataRoot.findall('Entry')) == 0:
                root.remove(metadataRoot)

            for tier in self:
                tierRoot = ET.SubElement(root, 'Tier')
                self.__format_tier(tierRoot, tier)

            for media in self.GetMedia():
                if media:
                    mediaRoot = ET.SubElement(root, 'Media')
                    self.__format_media(mediaRoot, media)

            hierarchyRoot = ET.SubElement(root, 'Hierarchy')
            self.__format_hierarchy(hierarchyRoot, self._hierarchy)

            for vocabulary, tierList in self.GetCtrlVocabs():
                vocabularyRoot = ET.SubElement(root, 'Vocabulary')
                XRA.__format_vocabulary(vocabularyRoot, vocabulary, tierList)

            indent(root)

            tree = ET.ElementTree(root)
            tree.write(filename, encoding=encoding, method="xml")

        except Exception:
            #import traceback
            #print(traceback.format_exc())
            raise

    # End write
    # -----------------------------------------------------------------

    def __format_media(self, mediaRoot, media):
        # Set attribute
        mediaRoot.set('id', media.id)
        mediaRoot.set('url', media.url)
        mediaRoot.set('mimetype', media.mime)

        # Element Tier
        for tier in self:
            if tier.GetMedia() == media:
                tierNode = ET.SubElement(mediaRoot, 'Tier')
                tierNode.set('id', self.__tier_id_map[tier])

        # Element Metadata
        if len(media.metadata.keys())>0:
            metadataRoot = ET.SubElement(mediaRoot, 'Metadata')
            self.__format_metadata(metadataRoot, media.metadata)

        # Element Content
        if len(media.content)>0:
            contentNode = ET.SubElement(mediaRoot, 'Content')
            contentNode.text = media.content

    # -----------------------------------------------------------------

    def __format_hierarchy(self, hierarchyRoot, hierarchy):
        try:
            for type in Hierarchy.hierarchy_types:
                for (former, latter) in hierarchy.getHierarchy(type):
                    link = ET.SubElement(hierarchyRoot, 'Link')
                    link.set('type', type)
                    # FIXME: this shouldn't be used because it breaks transaction unicity
                    link.set('from', self.__tier_id_map[former])
                    link.set('to', self.__tier_id_map[latter])
        except KeyError:
            #print('The current Hierarchy is invalid.')
            hierarchyRoot.clear()

    # -----------------------------------------------------------------

    @staticmethod
    def __format_vocabulary(vocabularyRoot, vocabulary, tierList):
        vocabularyRoot.set('id', vocabulary.GetIdentifier())
        vocabularyRoot.set('description', vocabulary.GetDescription())
        for entry in vocabulary:
            entryNode = ET.SubElement(vocabularyRoot, 'Entry')
            entryNode.text = unicode(entry.Value)
        for tier in tierList:
            tierNode = ET.SubElement(vocabularyRoot, 'Tier')
            tierNode.set('id', self.__tier_id_map[tier])

    # -----------------------------------------------------------------

    @staticmethod
    def __format_metadata(metadataRoot, metaObject):
        for key, value in metaObject.metadata.iteritems():
            entry = ET.SubElement(metadataRoot, 'Entry')
            entry.set('key', key)
            entry.text = unicode(value)

    # -----------------------------------------------------------------

    def __format_tier(self, tierRoot, tier):
        id = gen_id() #'t%d' % self.__tier_counter
        tierRoot.set("id", id)
        tier.metadata [ 'id' ] = id
        self.__tier_id_map[tier] = id
        self.__tier_counter += 1
        tierRoot.set("tiername", tier.GetName())

        metadataRoot = ET.SubElement(tierRoot, 'Metadata')
        XRA.__format_metadata(metadataRoot, tier)
        if len(metadataRoot.findall('Entry')) == 0:
            tierRoot.remove(metadataRoot)

        for annotation in tier:
            annotationRoot = ET.SubElement(tierRoot, 'Annotation')
            XRA.__format_annotation(annotationRoot, annotation)

        # TODO: add medias somehow

    # -----------------------------------------------------------------

    @staticmethod
    def __format_annotation(annotationRoot, annotation):
        locationRoot = ET.SubElement(annotationRoot, 'Location')
        XRA.__format_location(locationRoot,
                              annotation.GetLocation())

        labelRoot = ET.SubElement(annotationRoot, 'Label')
        XRA.__format_label(labelRoot, annotation.GetLabel())

    # -----------------------------------------------------------------

    @staticmethod
    def __format_label(labelRoot, label):
        labelRoot.set('scoremode', label.GetFunctionScore().__name__)
        for text in label.GetLabels():
            textNode = ET.SubElement(labelRoot, 'Text')
            XRA.__format_text(textNode, text)

    # -----------------------------------------------------------------

    @staticmethod
    def __format_text(textNode, text):
        textNode.set('score', unicode(text.GetScore()))

        typedValue = text.GetTypedValue()
        if isinstance(typedValue, int):
            textNode.set('type', 'int')
        elif isinstance(typedValue, float):
            textNode.set('type', 'float')
        elif isinstance(typedValue, bool):
            textNode.set('type', 'bool')
        elif isinstance(typedValue, str):
            textNode.set('type', 'str')

        textNode.text = text.GetValue()

    # -----------------------------------------------------------------

    @staticmethod
    def __format_location(locationRoot, location):
        for localization in location:
            localizationRoot = ET.SubElement(locationRoot,
                                             'Localization')
            XRA.__format_localization(localizationRoot, localization)

    # -----------------------------------------------------------------

    @staticmethod
    def __format_localization(localizationRoot, localization):
        localizationRoot.set('score', unicode(localization.GetScore()))
        if localization.IsTimePoint():
            point = ET.SubElement(localizationRoot, 'timepoint')
            XRA.__format_point(point, localization.GetPoint())

        elif localization.IsTimeInterval():
            intervalRoot = ET.SubElement(localizationRoot, 'timeinterval')
            XRA.__format_interval(intervalRoot, localization.GetPlace())

        elif localization.IsTimeDisjoint():
            disjointRoot = ET.SubElement(localizationRoot, 'timedisjoint')
            XRA.__format_disjoint(disjointRoot, localization.GetPlace())

        elif localization.IsFramePoint():
            framePoint = ET.SubElement(localizationRoot, 'framepoint')
            XRA.__format_point(framePoint, localization.GetPoint())

        elif localization.IsFrameInterval():
            intervalRoot = ET.SubElement(localizationRoot, 'frameinterval')
            XRA.__format_interval(intervalRoot, localization.GetPlace())

        elif localization.IsFrameDisjoint():
            disjointRoot = ET.SubElement(localizationRoot, 'framedisjoint')
            XRA.__format_disjoint(disjointRoot, localization.GetPlace())

        else:
            raise Exception("Localization is not a valid type")

    # -----------------------------------------------------------------

    @staticmethod
    def __format_point(pointNode, point):
        pointNode.set('midpoint', unicode(point.GetMidpoint()))
        pointNode.set('radius', unicode(point.GetRadius()))

    # -----------------------------------------------------------------

    @staticmethod
    def __format_interval(intervalRoot, interval):
        begin = ET.SubElement(intervalRoot, 'Begin')
        XRA.__format_point(begin, interval.GetBegin())

        end = ET.SubElement(intervalRoot, 'End')
        XRA.__format_point(end, interval.GetEnd())

    # -----------------------------------------------------------------

    @staticmethod
    def __format_disjoint(disjointRoot, disjoint):
        for interval in disjoint:
            intervalRoot = ET.SubElement(disjointRoot, 'Interval')
            XRA.__format_interval(intervalRoot, interval)

    # -----------------------------------------------------------------
