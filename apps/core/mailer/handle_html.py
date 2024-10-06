__all__ = ['HTMLController']

import re
from html import unescape

import minify_html
import nh3
from bs4 import BeautifulSoup
from django.conf import settings

from apps.shared.extends.utils import DictHandler
from apps.shared.html_constant import (
    SANITIZE_HTML_CONFIG_TAGS, SANITIZE_HTML_CONFIG_ATTRS,
    SANITIZE_HTML_CONFIG_ATTRS_PREFIX, SANITIZE_HTML_LINK_REL, SANITIZE_HTML_TAG_ATTRIBUTE_VALUES,
    SANITIZE_HTML_SET_TAG_ATTRIBUTE_VALUES,
)


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


class ManualNH3:  # pylint: disable=R0902
    # Ref: https://nh3.readthedocs.io/en/latest/

    @property
    def nh3_tags(self):
        return self._nh3_tags

    @nh3_tags.setter
    def nh3_tags(self, append_tags: set[str]):
        self._nh3_tags = self._nh3_tags.union(append_tags)

    @property
    def nh3_attributes(self):
        return self._nh3_attributes

    @nh3_attributes.setter
    def nh3_attributes(self, append_attrs: dict[str, set[str]]):
        if '*' not in self._nh3_attributes:
            self._nh3_attributes['*'] = set({})
        self._nh3_attributes['*'] = self._nh3_attributes['*'].union({'style', 'class', 'id'})

        # table
        if 'table' not in self._nh3_attributes:
            self._nh3_attributes['table'] = set({})
        self._nh3_attributes['table'] = self._nh3_attributes['table'].union({'border'})

        # span (tag element fill)
        if 'span' not in self._nh3_attributes:
            self._nh3_attributes['span'] = set({})
        self._nh3_attributes['span'] = self._nh3_attributes['span'].union({'data-code'})

        if append_attrs:
            for key, value in append_attrs.items():
                if isinstance(key, str) and isinstance(value, set):
                    if key in self._nh3_attributes:
                        self._nh3_attributes[key] = self._nh3_attributes[key].union(value)
                    else:
                        self._nh3_attributes[key] = value

    @property
    def generic_attribute_prefixes(self):
        return self._generic_attribute_prefixes

    @generic_attribute_prefixes.setter
    def generic_attribute_prefixes(self, generic_attribute_prefixes: set[str]):
        self._generic_attribute_prefixes = self._generic_attribute_prefixes.union(generic_attribute_prefixes)

    @property
    def link_rel(self):
        return self._link_rel

    @link_rel.setter
    def link_rel(self, link_rel: str):
        self._link_rel = link_rel

    @property
    def tag_attribute_values(self):
        return self._tag_attribute_values

    @tag_attribute_values.setter
    def tag_attribute_values(self, tag_attribute_values: dict[str, dict[str, set[str]]]):
        for ele, ele_value in tag_attribute_values.items():
            if ele not in self._tag_attribute_values:
                self._tag_attribute_values[ele] = {}
            for attr, attr_value in ele_value.items():
                if attr not in self._tag_attribute_values[ele]:
                    self._tag_attribute_values[ele][attr] = set([])
                self._tag_attribute_values[ele][attr] = self._tag_attribute_values[ele][attr].union(attr_value)

    @property
    def set_tag_attribute_values(self):
        return self._set_tag_attribute_values

    @set_tag_attribute_values.setter
    def set_tag_attribute_values(self, set_tag_attribute_values: dict[str, dict[str, str]]):
        for ele, ele_value in set_tag_attribute_values.items():
            if ele not in self._set_tag_attribute_values:
                self._set_tag_attribute_values[ele] = {}
            for attr, attr_value in ele_value.items():
                self._set_tag_attribute_values[ele][attr] = attr_value

    def __init__(self, html_str: str, **kwargs):
        self._nh3_tags: set[str] = {
            'code', 'dl', 'rp', 'hr', 'th', 'time', 'h2', 'u', 'br', 'li', 'header', 'tt',
            'strike', 'data', 'ol', 'sup', 'blockquote', 'td', 'h5', 'col', 'tbody', 'pre',
            'bdo', 'abbr', 'div', 'h4', 'var', 'table', 'small', 'h1', 'dt', 'area', 'ruby',
            's', 'p', 'em', 'summary', 'article', 'caption', 'details', 'colgroup', 'dd',
            'samp', 'thead', 'sub', 'b', 'figcaption', 'hgroup', 'tr', 'map', 'aside', 'q',
            'ins', 'span', 'i', 'rt', 'del', 'kbd', 'strong', 'a', 'acronym', 'dfn', 'wbr',
            'ul', 'rtc', 'bdi', 'figure', 'cite', 'center', 'footer', 'mark', 'h6', 'nav',
            'img', 'h3'
        }
        self._nh3_attributes: dict[str, set[str]] = {
            'q': {'cite'}, 'thead': {'charoff', 'align', 'char'}, 'a': {'href', 'hreflang'},
            'tbody': {'charoff', 'align', 'char'}, 'tfoot': {'charoff', 'align', 'char'},
            'th': {'charoff', 'headers', 'align', 'scope', 'colspan', 'rowspan', 'char'},
            'img': {'alt', 'align', 'src', 'width', 'height'}, 'tr': {'charoff', 'align', 'char'},
            'table': {'charoff', 'align', 'char', 'summary'}, 'col': {'charoff', 'span', 'align', 'char'},
            'del': {'cite', 'datetime'}, 'ol': {'start'}, 'hr': {'width', 'align', 'size'}, 'blockquote': {'cite'},
            'colgroup': {'charoff', 'span', 'align', 'char'}, 'ins': {'cite', 'datetime'},
            'td': {'headers', 'charoff', 'align', 'colspan', 'rowspan', 'char'}, 'bdo': {'dir'}
        }
        self._generic_attribute_prefixes: set[str] = set([])
        self._link_rel: str = ''
        self._tag_attribute_values: dict[str, dict[str, set[str]]] = {}
        self._set_tag_attribute_values: dict[str, dict[str, str]] = {}

        self.html_str: str = html_str
        self.soup = BeautifulSoup(html_str, 'html.parser')

        self.INPUT_NAME_ALLOWED: set[str] = set([])  # pylint: disable=C0103
        self.LINK_TRUSTED_DOMAIN: set[str] = set([]) # pylint: disable=C0103

        for key, value in kwargs.items():
            if key.startswith('override__'):
                key_tmp = key.replace('override__', '')
                setattr(self, key_tmp, value)
            else:
                setattr(self, key, value)

    @staticmethod
    def bastion_attribute_filter(  # pylint: disable=R0912
            element, attribute, value,
            inputs_name_allowed: set[str] = None,
            iframe_trusted_domain: set[str] = None
    ):
        if not inputs_name_allowed:
            inputs_name_allowed = set([])
        if not iframe_trusted_domain:
            iframe_trusted_domain = set([])

        if not inputs_name_allowed:
            inputs_name_allowed = []
        if element == ['input', 'select', 'textarea']:
            if attribute == 'name':
                if value not in inputs_name_allowed:
                    return None
            elif attribute == 'type':
                if value == 'submit':
                    return None
        elif element == 'button':
            if attribute == 'type':
                if value == 'submit':
                    return 'button'
        elif element == 'iframe':
            if attribute == 'src':
                if value.startswith("https://"):
                    domain = value.replace('https://', '').split('/')[0].lower()
                    if domain:
                        if domain in iframe_trusted_domain:
                            return value
                return None
        return value

    def nh3_attribute_filter(self, element, attribute, value):  # pylint: disable=R1710
        # return None was remove attribute it!
        # return data push it to value of attribute
        # --> Failed case: none return some element don't keep attribute and value
        # ----> Always return value : None | Other Value | Keep Value
        valid = self.bastion_attribute_filter(
            element, attribute, value,
            inputs_name_allowed=self.INPUT_NAME_ALLOWED,
            iframe_trusted_domain=self.LINK_TRUSTED_DOMAIN,
        )
        if valid != value:
            return value

    def nh3_clean(self, **kwargs):
        return nh3.clean(  # pylint: disable=E1101
            self.html_str,
            tags=self.nh3_tags,
            attributes=self.nh3_attributes,
            generic_attribute_prefixes=self.generic_attribute_prefixes,
            link_rel=self.link_rel,
            tag_attribute_values=self.tag_attribute_values,
            set_tag_attribute_values=self._set_tag_attribute_values,
            # attribute_filter=self.nh3_attribute_filter,
            **kwargs,
        )

    @classmethod
    def nh3_clean_text(cls, data):
        return nh3.clean_text(data)  # pylint: disable=E1101

    @classmethod
    def nh3_is_html(cls, data):
        return nh3.is_html(data)  # pylint: disable=E1101


class HTMLController(ManualNH3, ManualBleach):  # pylint: disable=R0902
    @staticmethod
    def minify(data, **kwargs):
        # https://github.com/wilsonzlin/minify-html?tab=readme-ov-file
        # https://docs.rs/minify-html/latest/minify_html/struct.Cfg.html
        return minify_html.minify(data, **kwargs)  # pylint: disable=E1101

    @staticmethod
    def detect_escape(data):
        # true if escape was executed
        data = data.strip()
        if data.startswith('<'):
            return False
        if '<' in data or '>' in data:
            return False
        return True

    def __init__(self, html_str: str, is_unescape: bool = False, soup_pretty: bool = False):
        html_str = HTMLController.unescape(html_str) if is_unescape is True else html_str
        if soup_pretty is True:
            html_str = BeautifulSoup(html_str, "html.parser").prettify()
        super().__init__(html_str=html_str)

    def handle_params(self, data: dict):
        params = self.soup.select("span.params-data[data-code]")
        for result in params:
            key_code = result.attrs['data-code']
            if key_code:
                data_code = DictHandler().get(key=key_code, data=data)
                result.string = data_code
            else:
                result.string = ''

        if '_workflow' in data:
            for key in data['_workflow']:
                # find key in href
                elements_with_attrs = self.soup.find_all(href=True)
                for element in elements_with_attrs:
                    # Replace the placeholders in the href attribute
                    if key in element['href']:
                        element['href'] = element['href'].replace(key, data['_workflow'][key])
        return self

    def clean(
            self,
            is_minify: bool = True,
            is_escape: bool = True,
            allowed_input_names: list[str] = None,
            trusted_domain: list[str] = None,
            # argument for nh3.clean()
            append_tags: set[str] = None,
            append_attrs: dict[str, set[str]] = None,
            attr_prefix: set[str] = None,
            link_rel: str = None,
            tag_attribute_values: dict[str, dict[str, set]] = None,
            set_tag_attribute_values: dict[str, dict[str, str]] = None,
            **kwargs
    ):
        self.nh3_tags = append_tags if append_tags else SANITIZE_HTML_CONFIG_TAGS
        self.nh3_attributes = append_attrs if append_attrs else SANITIZE_HTML_CONFIG_ATTRS
        self.generic_attribute_prefixes = attr_prefix if attr_prefix else SANITIZE_HTML_CONFIG_ATTRS_PREFIX
        self.link_rel = link_rel if link_rel else SANITIZE_HTML_LINK_REL
        self.tag_attribute_values = tag_attribute_values if tag_attribute_values else SANITIZE_HTML_TAG_ATTRIBUTE_VALUES
        if set_tag_attribute_values:
            self.set_tag_attribute_values = set_tag_attribute_values
        else:
            self.set_tag_attribute_values = SANITIZE_HTML_SET_TAG_ATTRIBUTE_VALUES
        self.INPUT_NAME_ALLOWED = set(allowed_input_names if allowed_input_names else [])
        self.LINK_TRUSTED_DOMAIN = set(trusted_domain if trusted_domain else settings.TRUSTED_DOMAIN_LINK)

        data = self.nh3_clean(**kwargs)
        if is_minify:
            data = self.minify(
                data,
                keep_closing_tags=True,
                keep_spaces_between_attributes=True,
                keep_html_and_head_opening_tags=True,
            )
        if is_escape:
            return self.nh3_clean_text(data=data)
        return data

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
