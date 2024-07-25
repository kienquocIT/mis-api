SANITIZE_HTML_CONFIG_TAGS = {
    'label', 'input', 'textarea', 'select', 'option', 'button',
    'svg', 'path', 'circle',
    'iframe',
}
SANITIZE_HTML_CONFIG_ATTRS = {
    'label': {'for'},
    'input': {
        'type', 'name', 'placeholder', 'required', 'disabled', 'readonly', 'checked', 'value',
        'min', 'max', 'minlength', 'maxlength',
    },
    'textarea': {
        'name', 'cols', 'rows', 'placeholder', 'required', 'disabled', 'readonly',
        'minlength', 'maxlength',
    },
    'select': {'name', 'required', 'disabled', 'readonly', 'placeholder', 'multiple'},
    'option': {'value', 'selected', },
    'button': {'type'},
    'svg': {'xmlns', 'fill', 'class', 'viewBox'},
    'path': {'d', 'fill', },
    'circle': {'cx', 'cy', 'r', 'fill', },
    'iframe': {'src', 'width', 'height', 'frameborder', 'title', 'allowfullscreen'},
}
SANITIZE_HTML_CONFIG_ATTRS_PREFIX = {'data-'}
SANITIZE_HTML_CLEAN_CONTENT_TAGS = {"script", "style", "hr", "br", "iframe"}  # clean_content_tags
SANITIZE_HTML_LINK_REL = "noopener noreferrer nofollow"
SANITIZE_HTML_TAG_ATTRIBUTE_VALUES = {
    'button': {
        'type': {'button'},
    }
}
SANITIZE_HTML_SET_TAG_ATTRIBUTE_VALUES = {
    'link': {
        'rel': "preload",
    },
    'iframe': {
        'loading': "lazy",
        'frameborder': '0',
        'referrerpolicy': 'no-referrer',
        'sandbox': "allow-scripts allow-same-origin allow-presentation",
        # 'allow': "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture;
        # web-share",
    },
    'img': {
        'loading': "lazy",
    },
}
# for special form
FORM_SANITIZE_TRUSTED_DOMAIN_LINK = ['www.youtube.com', 'www.bflow.vn']
