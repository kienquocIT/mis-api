__all__ = ['HTMLController']

import re
from copy import deepcopy
from html import unescape

import minify_html
import nh3
from bs4 import BeautifulSoup

from apps.shared.extends.utils import DictHandler


class ManualBleach:
    # Ref: https://github.com/mozilla/bleach
    # soup: BeautifulSoup

    # import bleach  # deprecated
    # from functools import partial
    # from bleach.linkifier import LinkifyFilter
    # def _clean_bleach(self):  # deprecated
    #     cleaner = bleach.Cleaner(
    #         filters=[partial(LinkifyFilter)]
    #     )
    #     return cleaner.clean(self.soup.prettify())

    ...


class ManualNH3:
    # Ref: https://nh3.readthedocs.io/en/latest/
    soup: BeautifulSoup

    nh3_tags: set[str] = None

    def nh3_get_tags(self, append_tags: set[str] = None) -> set[str] or ValueError:
        if not self.nh3_tags:
            tags = deepcopy(nh3.ALLOWED_TAGS)  # pylint: disable=E1101
            if isinstance(tags, set):
                if append_tags and isinstance(append_tags, set):
                    tags = tags.union(append_tags)

                self.nh3_tags = tags
                return tags
            raise ValueError('NH3.ALLOWED_ATTRIBUTES return should be "dict[str, set[str]]"')
        return self.nh3_tags

    # @staticmethod
    # def nh3_attribute_filter(element, attr_name, attr_value, *args, **kwargs):
    #     # return None was remove attribute it!
    #     # return data push it to value of attribute
    #     return None

    nh3_attributes: dict[str, set[str]] = None

    def nh3_get_attributes(self, append_attrs: dict[str, set[str]] = None) -> dict[str, set[str]] or ValueError:
        if not self.nh3_attributes:  # pylint: disable=R1702
            attributes = deepcopy(nh3.ALLOWED_ATTRIBUTES)  # pylint: disable=E1101
            if isinstance(attributes, dict):
                # all tag element
                if '*' not in attributes:
                    attributes['*'] = set({})
                attributes['*'] = attributes['*'].union({'style', 'class', 'id'})

                # table
                if 'table' not in attributes:
                    attributes['table'] = set({})
                attributes['table'] = attributes['table'].union({'border'})

                # span (tag element fill)
                if 'span' not in attributes:
                    attributes['span'] = set({})
                attributes['span'] = attributes['span'].union({'data-code'})

                if append_attrs:
                    for key, value in append_attrs.items():
                        if isinstance(key, str) and isinstance(value, set):
                            if key in attributes:
                                attributes[key] = attributes[key].union(value)
                            else:
                                attributes[key] = value
                self.nh3_attributes = attributes
                return attributes
            raise ValueError('NH3.ALLOWED_ATTRIBUTES return should be "dict[str, set[str]]"')
        return self.nh3_attributes

    def nh3_clean(self, append_tags, append_attrs, **kwargs):
        return nh3.clean(  # pylint: disable=E1101
            self.soup.prettify(),
            tags=self.nh3_get_tags(append_tags),
            attributes=self.nh3_get_attributes(append_attrs),
            **kwargs,
        )

    @classmethod
    def soup_clean_input(cls, html_str: str, allowed_names: list[str]):
        if html_str and allowed_names:
            soup = BeautifulSoup(html_str, "html.parser")
            inputs = soup.find_all('input')
            for input_tag in inputs:
                name_value = input_tag.get('name')
                if name_value not in allowed_names:
                    input_tag.decompose()
            return soup.prettify()
        return html_str

    @classmethod
    def nh3_clean_text(cls, data):
        return nh3.clean_text(data)  # pylint: disable=E1101

    @classmethod
    def nh3_is_html(cls, data):
        return nh3.is_html(data)  # pylint: disable=E1101


class HTMLController(ManualNH3, ManualBleach):
    @staticmethod
    def minify(data):
        return minify_html.minify(data)  # pylint: disable=E1101

    @staticmethod
    def detect_escape(data):
        # true if escape was executed
        data = data.strip()
        if data.startswith('<'):
            return False
        if '<' in data or '>' in data:
            return False
        return True

    def __init__(self, html_str: str, is_unescape: bool = False):
        self.html_str = HTMLController.unescape(html_str) if is_unescape is True else html_str
        self.soup = BeautifulSoup(self.html_str, "html.parser")

    def handle_params(self, data: dict):
        params = self.soup.select("span.params-data[data-code]")
        for result in params:
            key_code = result.attrs['data-code']
            if key_code:
                data_code = DictHandler().get(key=key_code, data=data)
                result.string = data_code
            else:
                result.string = ''
        return self

    def clean(
            self,
            append_tags: set[str] = None,
            append_attrs: dict[str, set[str]] = None,
            is_minify: bool = True,
            allowed_input_names: list[str] = None,
            **kwargs
    ):
        data = self.nh3_clean(
            append_tags=append_tags,
            append_attrs=append_attrs,
            **kwargs,
        )
        if allowed_input_names:
            data = self.soup_clean_input(html_str=data, allowed_names=allowed_input_names)
        if is_minify:
            data = self.minify(data)
        return self.nh3_clean_text(data=data)

    def is_html(self):
        return self.nh3_is_html(data=self.to_string())

    @staticmethod
    def unescape(data):
        result = unescape(data)
        return result

    def to_string(self):
        return self.soup.prettify()

    def get_all_font_family(self):
        styled_elements = self.soup.find_all(attrs={"style": True})
        font_family_regex = re.compile(r"font-family:\s*'(.*?)'")

        font_families = []
        for element in styled_elements:
            style_attr = element["style"]
            matches = font_family_regex.findall(style_attr)
            for match in matches:
                font_families.append(match)
        return font_families
