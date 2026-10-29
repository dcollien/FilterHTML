import re
import string
from html.parser import HTMLParser

def p2to3isunicode(s, t):
   """ Helper for python 2/3 to detect unicode string """
   try:
      return isinstance(s, unicode) or isinstance(t, unicode)  # p2
   except NameError:
      return isinstance(s, str) or isinstance(t, str)  # p3

def p2to3itervalues(g):
   """ Helper for itervalues """
   try:
      return g.itervalues()
   except AttributeError:
      return g.values()

def p2to3maketrans(a, b):
   try:
      return string.maketrans(a, b)
   except AttributeError:
      return str.maketrans(a, b)

PATTERN_TYPE = getattr(re, '_pattern_type', getattr(re, 'Pattern', None))

TRANS_TABLE = p2to3maketrans('','')

ATTR_NAME_MATCH = re.compile(r'^[a-z\-]+$')
CSS_ESCAPE = re.compile(r'^.*\\[0-9A-Fa-f].*$')
INVALID_ATTRIBUTE_REPLACEMENTS = {
   "url": "#",
   "url|empty": ""
}
UNSAFE_URL_CHARS = {
   " ": r"%20",
   "%": r"%25",
   ">": r"%3E",
   "<": r"%3C",
   "[": r"%5B",
   "]": r"%5D",
   "{": r"%7B",
   "}": r"%7D",
   "|": r"%7C",
   "\\": r"%5C",
   "^": r"%5E"
}

VOID_ELEMENTS = [
   'area',
   'base',
   'br',
   'col',
   'command',
   'embed',
   'hr',
   'img',
   'input',
   'keygen',
   'link',
   'meta',
   'param',
   'source',
   'track',
   'wbr',

   'basefont',
   'bgsound',
   'frame',
   'isindex'
]

HTML_ESCAPE_CHARS = {
   '>': '&gt;',
   '<': '&lt;',
   '&': '&amp;',
   ';': '&semi;',
}

HTML_ESCAPE_QUOTES = {
   '"': '&quot;',
   '\'': '&apos;',
}

ATTRIBUTE_ESCAPE_CHARS = {
   '>': '&gt;',
   '<': '&lt;',
   '&': '&amp;',
   '"': '&quot;',
   '\'': '&apos;',
}

TEXT_FILTER_ESCAPE_CHARS = {
   '>': '&gt;',
   '<': '&lt;',
   '&': '&amp;',
}

URL_ENCODING_MATCH = re.compile(r'(\%[0-9a-fA-F]{2})')
ENTITY_MATCH = re.compile(r'(\&[\#\d\w]+;)')

# predefined HTML colors
HTML_COLORS = frozenset([
   'aliceblue',
   'antiquewhite',
   'aqua',
   'aquamarine',
   'azure',
   'beige',
   'bisque',
   'black',
   'blanchedalmond',
   'blue',
   'blueviolet',
   'brown',
   'burlywood',
   'cadetblue',
   'chartreuse',
   'chocolate',
   'coral',
   'cornflowerblue',
   'cornsilk',
   'crimson',
   'cyan',
   'darkblue',
   'darkcyan',
   'darkgoldenrod',
   'darkgray',
   'darkgreen',
   'darkkhaki',
   'darkmagenta',
   'darkolivegreen',
   'darkorange',
   'darkorchid',
   'darkred',
   'darksalmon',
   'darkseagreen',
   'darkslateblue',
   'darkslategray',
   'darkturquoise',
   'darkviolet',
   'deeppink',
   'deepskyblue',
   'dimgray',
   'dimgrey',
   'dodgerblue',
   'firebrick',
   'floralwhite',
   'forestgreen',
   'fuchsia',
   'gainsboro',
   'ghostwhite',
   'gold',
   'goldenrod',
   'gray',
   'green',
   'greenyellow',
   'honeydew',
   'hotpink',
   'indianred',
   'indigoivory',
   'khaki',
   'lavender',
   'lavenderblush',
   'lawngreen',
   'lemonchiffon',
   'lightblue',
   'lightcoral',
   'lightcyan',
   'lightgoldenrodyellow',
   'lightgray',
   'lightgreen',
   'lightpink',
   'lightsalmon',
   'lightseagreen',
   'lightskyblue',
   'lightslategray',
   'lightsteelblue',
   'lightyellow',
   'lime',
   'limegreen',
   'linen',
   'magenta',
   'maroon',
   'mediumaquamarine',
   'mediumblue',
   'mediumorchid',
   'mediumpurple',
   'mediumseagreen',
   'mediumslateblue',
   'mediumspringgreen',
   'mediumturquoise',
   'mediumvioletred',
   'midnightblue',
   'mintcream',
   'mistyrose',
   'moccasin',
   'navajowhite',
   'navy',
   'oldlace',
   'olive',
   'olivedrab',
   'orange',
   'orangered',
   'orchid',
   'palegoldenrod',
   'palegreen',
   'paleturquoise',
   'palevioletred',
   'papayawhip',
   'peachpuff',
   'peru',
   'pink',
   'plum',
   'powderblue',
   'purple',
   'red',
   'rosybrown',
   'royalblue',
   'saddlebrown',
   'salmon',
   'sandybrown',
   'seagreen',
   'seashell',
   'sienna',
   'silver',
   'skyblue',
   'slateblue',
   'slategray',
   'snow',
   'springgreen',
   'steelblue',
   'tan',
   'teal',
   'thistle',
   'tomato',
   'turquoise',
   'violet',
   'wheat',
   'white',
   'whitesmoke',
   'yellow',
   'yellowgreen'
])

# different HTML color formats
HEX_MATCH = re.compile(r'^#([0-9A-Fa-f]{3}){1,2}$')

RGB_MATCH = re.compile(r'^rgb\(\s*\d+%?\s*,\s*\d+%?\s*,\s*\d+%?\s*\)$')

RGBA_MATCH = re.compile(r'^rgba\(\s*\d+%?\s*,\s*\d+%?\s*,\s*\d+%?\s*,\s*(\d+\.)?\d+\s*\)$')

HSL_MATCH = re.compile(r'^hsl\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*\)$')

HSLA_MATCH = re.compile(r'^hsla\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*,\s*(\d+\.)?\d+\s*\)$')

MEASUREMENT_MATCH = re.compile(r'^(-?\d+(px|cm|pt|em|ex|pc|mm|in)?|\d+%)$')

# Kept so existing except clauses still work; bad nesting is now repaired instead of raised.
class TagMismatchError(Exception):
   pass

class HTMLSyntaxError(Exception):
   pass

class _Element(object):
   def __init__(self, name, attrs):
      self.name = name
      self.attrs = attrs
      self.children = []

class _TreeBuilder(HTMLParser):
   """ Builds a tree of _Element and text nodes, repairing bad nesting """
   def __init__(self):
      HTMLParser.__init__(self, convert_charrefs=True)
      self.root = _Element(None, [])
      self.open_elements = [self.root]

   def handle_starttag(self, tag, attrs):
      element = _Element(tag, attrs)
      self.open_elements[-1].children.append(element)
      if tag not in VOID_ELEMENTS:
         self.open_elements.append(element)

   def handle_startendtag(self, tag, attrs):
      # like browsers, ignore "/>" on non-void elements
      self.handle_starttag(tag, attrs)

   def handle_endtag(self, tag):
      # close the nearest matching open element; ignore stray closing tags
      for i in range(len(self.open_elements) - 1, 0, -1):
         if self.open_elements[i].name == tag:
            del self.open_elements[i:]
            return

   def handle_data(self, data):
      self.open_elements[-1].children.append(data)

def _parse(html):
   builder = _TreeBuilder()
   builder.feed(html)
   builder.close()
   return builder.root.children

def _escape(value, table):
   return ''.join(table.get(char, char) for char in value)

class HTMLFilter(object):
   def __init__(self, spec, allowed_schemes=('http', 'https', 'mailto', 'ftp'), text_filter=None, remove=None):
      self.trans_table = TRANS_TABLE
      self.removals = remove

      if self.removals is None:
         # by default scripts and styles are removed if they don't exist in the spec
         self.removals = []
         if 'script' not in spec:
            self.removals.append('script')
         if 'style' not in spec:
            self.removals.append('style')

      self.allowed_schemes = allowed_schemes

      self.text_filter = text_filter

      # allow global attributes
      if '*' in spec:
         self.global_attrs = spec['*']
      else:
         self.global_attrs = {}

      self.spec = spec

   def filter(self, html):
      return self.__filter_nodes(_parse(html), [], self.text_filter)

   def __filter_nodes(self, nodes, tag_stack, text_filter):
      output = []

      for node in nodes:
         if isinstance(node, _Element):
            output.append(self.__filter_element(node, tag_stack, text_filter))
         elif text_filter is not None:
            filtered_text = text_filter(_escape(node, TEXT_FILTER_ESCAPE_CHARS), tag_stack)

            # the text filter returns HTML, which must also adhere to the spec
            output.append(self.__filter_nodes(_parse(filtered_text), tag_stack, None))
         else:
            output.append(_escape(node, HTML_ESCAPE_CHARS))

      return ''.join(output)

   def __filter_element(self, element, tag_stack, text_filter):
      if element.name in self.removals:
         return ''

      tag_spec = self.__get_tag_spec(element.name, tag_stack)

      if tag_spec is None:
         # remove the tag, keep its contents
         return self.__filter_nodes(element.children, tag_stack, text_filter)

      if tag_spec == False:
         # remove the tag and its contents
         return ''

      tag_name, attributes = self.__follow_aliases(element.name)
      attributes += self.__filter_attributes(tag_name, element.attrs, tag_stack)

      tag_output = '<' + tag_name
      if len(attributes) > 0:
         tag_output += ' ' + ' '.join(attributes)
      tag_output += '>'

      if tag_name in VOID_ELEMENTS:
         return tag_output

      if element.name == 'script' and tag_name == 'script':
         # the spec explicitly allows scripts, so their contents pass through unchanged
         contents = ''.join(child for child in element.children if not isinstance(child, _Element))
      else:
         contents = self.__filter_nodes(element.children, tag_stack + [(tag_name, attributes)], text_filter)

      return '%s%s</%s>' % (tag_output, contents, tag_name)

   def __get_tag_spec(self, tag_name, tag_stack):
      tag_spec = self.spec.get(tag_name, None)

      if callable(tag_spec):
         tag_spec = tag_spec(tag_name, tag_stack)

      return tag_spec

   def __escape_data(self, char, include_quotes=False):
      if char in HTML_ESCAPE_CHARS:
         return HTML_ESCAPE_CHARS[char]
      elif include_quotes and char in HTML_ESCAPE_QUOTES:
         return HTML_ESCAPE_QUOTES[char]
      else:
         return char

   def __follow_aliases(self, tag_name):
      alias_attributes = []
      while tag_name in self.spec and isinstance(self.spec[tag_name], str):
         tag_parts = self.spec[tag_name].split(' ') # follow aliases
         tag_name = tag_parts[0]
         if len(tag_parts) > 1:
            alias_attributes += tag_parts[1:]

      return tag_name, alias_attributes

   def __filter_attributes(self, tag_name, attrs, tag_stack):
      tag_spec = self.__get_tag_spec(tag_name, tag_stack)
      if not isinstance(tag_spec, dict):
         tag_spec = {}

      attributes = []
      seen = set()

      for attribute_name, value in attrs:
         # browsers keep the first of any repeated attribute
         if attribute_name in seen or not ATTR_NAME_MATCH.match(attribute_name):
            continue
         seen.add(attribute_name)

         # a value-less attribute (e.g. "checked") has the empty string as its value
         if value is None:
            value = ''

         new_value = self.__filter_value(tag_spec, attribute_name, value)
         if new_value is True:
            attributes.append(attribute_name)
         elif new_value is not None:
            attributes.append('%s="%s"' % (attribute_name, _escape(new_value, ATTRIBUTE_ESCAPE_CHARS)))

      return attributes

   def __filter_value(self, tag_spec, attribute_name, value):
      rules = None
      global_rules = None

      # retrieve element-specific rules for this attribute
      if attribute_name in tag_spec:
         rules = tag_spec[attribute_name]
      elif '*' in tag_spec:
         rules = tag_spec['*']
      elif '^$' in tag_spec:
         for pair in tag_spec['^$']:
            if isinstance(pair, list):
               regex, pair_rules = pair
               if isinstance(regex, PATTERN_TYPE) and regex.match(attribute_name):
                  rules = pair_rules
                  break
      else:
         for regex, regex_rules in tag_spec.items():
            if isinstance(regex, PATTERN_TYPE) and regex.match(attribute_name):
               rules = regex_rules
               break

      # retrieve rules for this attribute global to all elements
      if attribute_name in self.global_attrs:
         global_rules = self.global_attrs[attribute_name]

      # at least some rules must exist to continue
      if rules is None and global_rules is None:
         return None

      new_value = None
      # purify the attribute value using the element-specific rules
      if rules is not None:
         new_value = self.__purify_attribute(attribute_name, value, rules)

      # if it filtered out the value, try the global rules for this attribute
      if global_rules is not None and (new_value is None or new_value == ''):
         new_value = self.__purify_attribute(attribute_name, value, global_rules)

      if new_value is None or new_value is True:
         return new_value
      else:
         return str(new_value)

   def __purify_attribute(self, attribute_name, value, rules):
      
      value, purified = self.purify_value(value, rules, attribute_name=attribute_name)

      if not purified:
         if attribute_name == "class" and isinstance(rules, list):
            candidate_values = value.split(' ')
            allowed_values_set = set()
            allowed_values = []

            for candidate in candidate_values:
               for rule in rules:
                  new_class_value = None
                  if isinstance(rule, PATTERN_TYPE):
                     new_class_value = self.purify_regex(candidate, rule)
                  elif callable(rule):
                     new_class_value = rule(value)
                  elif candidate == rule:
                     new_class_value = candidate

                  if new_class_value and new_class_value not in allowed_values_set:
                     allowed_values_set.add(new_class_value)
                     allowed_values.append(new_class_value)

            if len(allowed_values) > 0:
               value = ' '.join(allowed_values)
            else:
               value = None
         elif attribute_name == "style" and isinstance(rules, dict):
            candidate_values = value.split(';')

            # map purify_style over each style
            allowed_values = [self.purify_style(style, rules) for style in candidate_values]
            
            # filter out invalid styles
            allowed_values = [style_value for style_value in allowed_values if style_value]

            if len(allowed_values) > 0:
               value = ';'.join(allowed_values) + ';'
            else:
               value = None
         elif value not in rules:
            value = None

      return value

   def purify_value(self, value, rules, attribute_name=None):
      purified = True

      if rules == "*":
         # leave the value as-is
         value = value
      elif isinstance(rules, PATTERN_TYPE):
         value = self.purify_regex(value, rules)
      elif rules == "boolean":
         if value == "" or (attribute_name is not None and value == attribute_name):
            value = True
         else:
            value = None
      elif rules == "url":
         value = value.strip()
         value = self.purify_url(value)
      elif rules == "url|empty":
         value = value.strip()
         if value != '':
            value = self.purify_url(value)
      elif rules == "color":
         value = self.purify_color(value)
      elif rules == "measurement":
         value = self.purify_regex(value, MEASUREMENT_MATCH)
      elif rules == "int":
         value = self.purify_int(value)
      elif rules == "alpha":
         if value == '':
            value = None
         else:
            value = self.purify_set(value, string.ascii_letters)
      elif rules == "alphanumeric":
         if value == '':
            value = None
         else:
            value = self.purify_set(value, string.ascii_letters + string.digits)
      elif rules == "alpha|empty":
         if value != '':
            value = self.purify_set(value, string.ascii_letters)
      elif rules == "alphanumeric|empty":
         if value != '':
            value = self.purify_set(value, string.ascii_letters + string.digits)
      elif rules == "text":
         # any text is allowed; it is HTML-encoded on output
         value = value
      elif isinstance(rules, str) and rules.startswith('[') and rules.endswith(']'):
         if value == '':
            value = None
         else:
            value = self.purify_set(value, rules[1:-1])
      elif callable(rules):
         value = rules(value)
      else:
         purified = False

      if value is None and isinstance(rules, str) and rules in INVALID_ATTRIBUTE_REPLACEMENTS:
         value = INVALID_ATTRIBUTE_REPLACEMENTS[rules]

      return value, purified

   def __escape_pattern(self, pattern, value, escaper):
      entities = set(pattern.findall(value))
      new_text = []
      for chunk in pattern.split(value):
         if chunk not in entities:
            chunk = ''.join([escaper(char) for char in chunk])
         new_text.append(chunk)

      return ''.join(new_text)

   def purify_style(self, style, rules):
      assert isinstance(rules, dict)

      parts = style.split(':')

      if len(parts) != 2:
         return None

      name = parts[0].strip()
      value = parts[1].strip()

      if CSS_ESCAPE.match(value):
         # disallow CSS unicode escaping
         return None

      if name in rules:
         style_rules = rules[name]
         value, purified = self.purify_value(value, style_rules)
         if not purified:
            if value not in style_rules:
               return None
         elif value is None or value == '':
            return None
      else:
         return None

      return ':'.join([name, value])

   def purify_color(self, value):
      value = value.lower()

      if value in HTML_COLORS:
         return value

      if HEX_MATCH.match(value):
         return value

      if RGB_MATCH.match(value):
         return value

      if RGBA_MATCH.match(value):
         return value

      if HSL_MATCH.match(value):
         return value

      if HSLA_MATCH.match(value):
         return value

      return None

   def purify_url(self, url):
      # encode unsafe characters
      def escaper(char):
         return UNSAFE_URL_CHARS.get(char, char)
      
      url = self.__escape_pattern(URL_ENCODING_MATCH, url, escaper)
      
      if '//' not in self.allowed_schemes and url.startswith('//'):
         return None # disallow protocol-relative URLs (possible XSS vector)

      parts = url.split(':')
      scheme = ''
      if len(parts) > 1:
         scheme = parts[0]
         if '/' in scheme or '#' in scheme:
            scheme = ''
            url = None
         else:
            url = ':'.join(parts[1:])

      if scheme == '':
         if url == '':
            return None
         else:
            return url
      elif scheme.lower() in self.allowed_schemes:
         return '%s:%s' % (scheme, url)
      else:
         return None

   def purify_int(self, value):
      try:
         return str(int(value))
      except ValueError:
         return None

   def purify_set(self, value, allowed_chars):
      if p2to3isunicode(value, allowed_chars):
         translation_table = dict.fromkeys(map(ord, allowed_chars), None)
         if value.translate(translation_table):
            value = None
      else:
         if value.translate(self.trans_table, allowed_chars):
            value = None

      return value
   
   def purify_regex(self, value, regex):
      if regex.match(value):
         return value
      else:
         return None

   def purify_text(self, value, include_quotes=False):
      def escaper(char):
         return self.__escape_data(char, include_quotes)
      
      return self.__escape_pattern(ENTITY_MATCH, value, escaper)

def filter_html(html, spec, **kwargs):
   html_filter = HTMLFilter(spec, **kwargs)
   return html_filter.filter(html)

