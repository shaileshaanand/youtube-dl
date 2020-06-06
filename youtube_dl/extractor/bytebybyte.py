# coding: utf-8
from __future__ import unicode_literals
from bs4 import BeautifulSoup
from .common import InfoExtractor
from .wistia import WistiaIE
import re


class ByteByByteIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?courses.byte-by-byte\.com/products/[^/]+/categories/[0-9]+/posts/(?P<id>[0-9]+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        webpage_soup = BeautifulSoup(webpage, 'html.parser')
        wistia_video_id = self._html_search_regex(r'id="wistia_([a-z0-9A-z]+)"', webpage, 'wistia_video_id', fatal=False)
        if wistia_video_id is None:
            return
        title = self._html_search_regex(r'<h1 [^>]+>([^<]+)</h1>', webpage, 'wistia_video_title')
        chapter = webpage_soup.select_one(".panel__body .panel__sub-title").text
        chapter_number = int(self._search_regex(r'([0-9]+)', chapter, 'chapter_number'))
        return {
            '_type': 'url_transparent',
            'ie_key': WistiaIE.ie_key(),
            'url': "wistia:{}".format(wistia_video_id),
            'title': title,
            'chapter': chapter,
            'chapter_number': chapter_number,
            'chapter_id': chapter_number,
        }


class ByteByByteCourseIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?courses\.byte-by-byte\.com/products/(?P<id>[^/]+)/?'

    def _real_extract(self, url):
        course_id = self._match_id(url)
        course_page = BeautifulSoup(self._download_webpage(url, course_id), 'html.parser')
        chapters = [x.get('href') for x in course_page.select(".panel.syllabus")[0].find_all('a')]
        entries = []
        for chapter_url in chapters:
            chapter_id = self._search_regex(r'([0-9]+)', chapter_url, chapter_url)
            chapter_page = self._download_webpage(chapter_url, chapter_id)
            lessons = re.findall(r'(\/products\/coding-interview-mastery-system-design\/categories\/[0-9]+\/posts\/[0-9]+)', chapter_page)
            for lesson in lessons:
                lesson_url = "https://courses.byte-by-byte.com" + lesson
                entries.append(
                    {
                        '_type': 'url_transparent',
                        'ie_key': ByteByByteIE.ie_key(),
                        'url': lesson_url,
                    }
                )
        return self.playlist_result(entries, course_id, course_id)
