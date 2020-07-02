# coding: utf-8
from __future__ import unicode_literals
import json
import re
from .common import InfoExtractor


class CxlIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?cxl\.com/institute/lesson/(?P<id>[^/]+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpagelines = self._download_webpage(url, video_id).split('\n')
        try:
            dataline = list(filter(lambda line: "cxlJWPlayerData" in line, webpagelines))[0].replace("\\", "").replace('"config":"', '"config":').replace('}","transcript', '},"transcript')
            data = json.loads(dataline[dataline.index("{"):-1])
        except IndexError:
            return
        formats = []
        for source in data["config"]["playlist"][0]["sources"]:
            if source["type"] == "video/mp4":
                formats.append({
                    "format": "mp4",
                    "format_id": source["label"],
                    "width": source["width"],
                    "height": source["height"],
                    "resolution": "{}x{}".format(source["width"], source["height"]),
                    "url": source["file"]
                })
        formats.sort(key=lambda format: format["width"])
        return {
            'id': data["mediaId"],
            'title': data["config"]["title"],
            'formats': formats
        }


class CxlCourseIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?cxl\.com/institute/course/(?P<id>[^/]+)'

    def _real_extract(self, url):
        course_id = self._match_id(url)
        course_page = self._download_webpage(url, course_id)
        title = self._html_search_regex(r'<title>(.+?)</title>', course_page, 'title')
        links = re.findall(r'https://cxl.com/institute/lesson/[^/]+', course_page)
        entries = []
        for link in links:
            entries.append({
                '_type': 'url_transparent',
                'url': link,
                'title': title,
                'ie_key': CxlIE.ie_key()
            })
        return self.playlist_result(entries, course_id, title)
