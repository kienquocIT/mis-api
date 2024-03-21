__all__ = ['HTMLController']

import re
from copy import deepcopy
from html import unescape

import nh3
from bs4 import BeautifulSoup

from apps.shared import StringHandler


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

    # @staticmethod
    # def nh3_attribute_filter(element, attr_name, attr_value, *args, **kwargs):
    #     # return None was remove attribute it!
    #     # return data push it to value of attribute
    #     return None

    nh3_attributes: dict[str, set[str]] = None

    def nh3_get_attributes(self) -> dict[str, set[str]] or ValueError:
        if not self.nh3_attributes:
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

                self.nh3_attributes = attributes
                return attributes
            raise ValueError('NH3.ALLOWED_ATTRIBUTES return should be "dict[str, set[str]]"')
        return self.nh3_attributes

    def nh3_clean(self):
        return nh3.clean(  # pylint: disable=E1101
            self.soup.prettify(),
            attributes=self.nh3_get_attributes(),
        )

    @classmethod
    def nh3_clean_text(cls, data):
        return nh3.clean_text(data)  # pylint: disable=E1101

    @classmethod
    def nh3_is_html(cls, data):
        return nh3.is_html(data)  # pylint: disable=E1101


class HTMLController(ManualNH3, ManualBleach):
    def __init__(self, html_str):
        self.html_str = html_str
        self.soup = BeautifulSoup(html_str, "html.parser")

    def handle_params(self):
        # span.params-data[data-code]
        params = self.soup.select("span.params-data[data-code]")
        for result in params:
            _covert = (result.text, result.string)
            txt_replace = StringHandler.random_str(12)
            result.string = txt_replace
        return self

    def clean(self):
        return self.nh3_clean_text(data=self.nh3_clean())

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
