import re
import string

TRANS_TABLE = string.maketrans('','')
TAG_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz123456")
ATTR_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz-")
UNICODE_ESCAPE = '&#'
CSS_ESCAPE = re.compile(r'^.*\\[0-9A-Fa-f].*$')
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
   '"': '&quot;'
}

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

# states for navigating script tags (tag body contains "<" signs)
"""
   data
   skip-data
   script-data
   script-data-less-than-sign
"""

class TagMismatchError(Exception):
   pass

class HTMLSyntaxError(Exception):
   pass

class HTMLFilter(object):
   def __init__(self, spec, allowed_schemes=('http', 'https', 'mailto', 'ftp'), text_filter=None, remove=None):
      self.tag_chars = TAG_CHARS
      self.attr_chars = ATTR_CHARS
      self.trans_table = TRANS_TABLE
      self.tag_removing = None
      self.removals = remove

      if self.removals is None:
         # by default scripts and styles are removed if they don't exist in the spec
         self.removals = []
         if 'script' not in spec:
            self.removals.append('script')
         if 'style' not in spec:
            self.removals.append('style')

      self.remove_scripts = ('script' in self.removals)

      self.allowed_schemes = allowed_schemes

      self.text_filter = text_filter

      self.html = ''
      self.filtered_html = []
      self.state = 'data'

      # allow global attributes
      if '*' in spec:
         self.global_attrs = spec['*']
      else:
         self.global_attrs = []

      self.spec = spec


   def filter(self, html):
      self.html = html
      self.chars = self.__char_gen()
      self.filtered_html = []
      self.tag_stack = []

      text_chars = []
      while self.__next():
         if self.curr_char == '<':

            # filtered text
            filtered_text = self.__filter_text(text_chars)

            # start of tag
            tag_output = self.__filter_tag()

            if self.state == 'script-data-less-than-sign':
               # tag was not filtered, append the consumed text
               if not self.remove_scripts:
                  if 'script' in self.spec and isinstance(self.spec['script'], str):
                     text_chars.append(self.__escape_data('<'))
                  else:
                     text_chars.append('<')
                  text_chars.append(self.__escape_data(self.curr_char))

               self.state = 'script-data'
            else:
               self.filtered_html += filtered_text
               text_chars = []
               self.filtered_html.append(tag_output)
         else:
            if self.state == 'script-data' and self.remove_scripts:
               pass
            elif self.state == 'skip-data':
               pass
            else:
               # collect text characters and escape them
               text_chars.append(self.__escape_data(self.curr_char))

      # filter and add any leftover text
      self.filtered_html += self.__filter_text(text_chars)

      if len(self.tag_stack) != 0:
         error = 'Tags not closed: %s' % ', '.join(tag for tag, _ in self.tag_stack)
         raise TagMismatchError(error)

      return ''.join(self.filtered_html)

   def __escape_data(self, char):
      if char in HTML_ESCAPE_CHARS:
         return HTML_ESCAPE_CHARS[char]
      else:
         return char

   def __filter_text(self, text_chars):
      filtered_html = []

      # filter collected text
      # and save it into filtered_html
      if self.text_filter is not None:
         filtered_text = self.text_filter(''.join(text_chars), self.tag_stack)

         # ensure filtered text adheres to the html spec
         filtered_text = filter_html(filtered_text, self.spec, allowed_schemes=self.allowed_schemes, remove=self.removals)

         filtered_html += list(filtered_text)
      else:
         filtered_html += text_chars

      return filtered_html

   def __char_gen(self):
      self.curr_char = ''
      self.row = 0
      self.line = 0
      for c in self.html:
         self.curr_char = c
         yield c

         self.row += 1
         if c == '\n':
            self.line += 1
            self.row = 0

   def __next(self):
      try:
         return self.chars.next()
      except StopIteration:
         self.curr_char = ''
         return ''

   def __filter_tag(self):
      tag_output = ''

      assert self.curr_char == '<'

      self.__next()
      if self.curr_char == '/':
         self.__next()
         # </closing tag>, curr_char is first character of tag name
         tag_output = self.__filter_closing_tag()
      elif self.curr_char == '!' and self.state != 'script-data':
         # <!-- comment tag -->
         self.__extract_remaining_tag()
      else:
         # <opening tag>, curr_char is first character of tag name
         if self.state == 'script-data':
            self.state = 'script-data-less-than-sign'
         else:
            tag_output = self.__filter_opening_tag()

      assert (self.state == 'script-data-less-than-sign' or self.curr_char == '>' or self.curr_char == '')

      return tag_output

   def __extract_whitespace(self):
      whitespace = []

      if self.curr_char.isspace():
         whitespace.append(self.curr_char)
         while self.__next().isspace():
            whitespace.append(self.curr_char)

      return ''.join(whitespace)

   def __extract_tag_name(self):
      tag_name = []

      if self.curr_char.lower() in self.tag_chars:
         tag_name.append(self.curr_char.lower())
         while self.__next().lower() in self.tag_chars:
            tag_name.append(self.curr_char.lower())

      return ''.join(tag_name)

   def __extract_attribute_name(self):
      attr_name = []

      if self.curr_char.lower() in self.attr_chars:
         attr_name.append(self.curr_char.lower())
         while self.__next().lower() in self.attr_chars:
            attr_name.append(self.curr_char.lower())

      return ''.join(attr_name)

   def __extract_remaining_tag(self):
      remaining_tag = []

      if self.curr_char != '>':
         remaining_tag.append(self.curr_char)
         while self.__next() != '>' and self.curr_char != '':
            remaining_tag.append(self.curr_char)

      return ''.join(remaining_tag)

   def __follow_aliases(self, tag_name):
      alias_attributes = []
      while tag_name in self.spec and isinstance(self.spec[tag_name], str):
         tag_parts = self.spec[tag_name].split(' ') # follow aliases
         tag_name = tag_parts[0]
         if len(tag_parts) > 1:
            alias_attributes += tag_parts[1:]

      return tag_name, alias_attributes

   def __filter_opening_tag(self):
      tag_output = []

      self.__extract_whitespace()

      tag_name = self.__extract_tag_name()

      if tag_name == 'script':
         self.state = 'script-data'
      elif tag_name in self.removals:
         self.tag_removing = tag_name
         self.state = 'skip-data'

      tag_name, attributes = self.__follow_aliases(tag_name)
      
      if tag_name in self.spec:
         while self.curr_char != '>' and self.curr_char != '':
            self.__extract_whitespace()
            attribute = self.__filter_attribute(tag_name)
            if attribute is not None:
               attributes.append(attribute)

         tag_output = ['<%s' % (tag_name,)]

         if len(attributes) > 0:
            tag_output.append(' ' + ' '.join(attributes))

         tag_output.append('>')

         if tag_name not in VOID_ELEMENTS:
            self.tag_stack.append((tag_name, attributes))

      else:
         self.__extract_remaining_tag()

      return ''.join(tag_output)

   def __filter_closing_tag(self):
      tag_output = ''

      self.__extract_whitespace()

      tag_name = self.__extract_tag_name()

      if tag_name == 'script' and self.state == 'script-data':
         self.state = 'data'
      elif tag_name == self.tag_removing and self.state == 'skip-data':
         self.state = 'data'
         self.tag_removing == None
      
      tag_name, attributes = self.__follow_aliases(tag_name)

      if tag_name in self.spec and tag_name not in VOID_ELEMENTS:
         self.__extract_whitespace()
         if self.curr_char == '>':
            tag_output = '</%s>' % (tag_name,)

            if len(self.tag_stack) == 0:
               raise TagMismatchError('Closing tag </%s> not found %d:%d' % (tag_name, self.line, self.row)) 

            opening_tag_name, attributes = self.tag_stack.pop()
            if opening_tag_name != tag_name:
               raise TagMismatchError('Opening tag <%s> does not match closing tag </%s> %d:%d' % (opening_tag_name, tag_name, self.line, self.row))
      else:
         self.__extract_remaining_tag()

      return tag_output

   def __filter_attribute(self, tag_name):
      allowed_attributes = self.spec[tag_name].keys()
      
      attribute_name = self.__extract_attribute_name()
      
      whitespace = self.__extract_whitespace()

      is_allowed = (attribute_name in allowed_attributes) or (attribute_name in self.global_attrs)

      assignment = ''
      value = None
      if self.curr_char == '=':
         assignment = '='
         
         self.__next() # nom the =

         self.__extract_whitespace()
         value = self.__filter_value(tag_name, attribute_name)
         if value is None:
            is_allowed = False

      elif self.curr_char not in self.attr_chars and self.curr_char != '>':
         self.__next() # skip invalid characters
         is_allowed = False

      if is_allowed:
         return  '%s=%s' % (attribute_name, value)
      else:
         return None


   def __filter_value(self, tag_name, attribute_name):
      value_chars = []
      quote = '"'
      if self.curr_char == "'" or self.curr_char == '"':
         quote = self.curr_char

         while self.__next() != quote:
            if self.curr_char == '':
               raise HTMLSyntaxError('Attribute quote not closed: <' + tag_name + ' ' + attribute_name + '>')
               break

            value_chars.append(self.curr_char)

         # nom the quote
         self.__next()

      value = ''.join(value_chars)
      
      rules = None
      global_rules = None

      # retrieve element-specific rules for this attribute
      if attribute_name in self.spec[tag_name]:
         rules = self.spec[tag_name][attribute_name]

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

      if new_value is None or new_value == '':
         return None
      else:
         return '%s%s%s' % (quote, new_value, quote)

   def __purify_attribute(self, attribute_name, value, rules):
      
      value, purified = self.purify_value(value, rules)

      if not purified:
         if attribute_name == "class" and isinstance(rules, list):
            candidate_values = value.split(' ')
            allowed_values_set = set()
            allowed_values = []

            for candidate in candidate_values:
               for rule in rules:
                  new_class_value = None
                  if isinstance(rule, re._pattern_type):
                     new_class_value = self.purify_regex(candidate, rule)
                  elif callable(rule):
                     new_class_value = rule(value)
                  elif candidate == rule:
                     new_class_value = candidate

                  if new_class_value and new_class_value not in allowed_values_set:
                     allowed_values_set.add(new_class_value)
                     allowed_values.append(new_class_value)


            value = ' '.join(allowed_values)
         elif attribute_name == "style" and isinstance(rules, dict):
            candidate_values = value.split(';')

            # map purify_style over each style
            allowed_values = [self.purify_style(style, rules) for style in candidate_values]
            
            # filter out invalid styles
            allowed_values = [style_value for style_value in allowed_values if style_value]

            if len(allowed_values) > 0:
               value = ';'.join(allowed_values) + ';'
            else:
               value = ''
         elif value not in rules:
            value = ''

      return value

   def purify_value(self, value, rules):
      purified = True

      if UNICODE_ESCAPE in value:
         # disallow &# in values (can be used for encoding disallowed characters)
         value = None
      elif isinstance(rules, re._pattern_type):
         value = self.purify_regex(value, rules)
      elif rules == "url":
         value = self.purify_url(value)
      elif rules == "color":
         value = self.purify_color(value)
      elif rules == "measurement":
         value = self.purify_regex(value, MEASUREMENT_MATCH)
      elif rules == "int":
         value = self.purify_int(value)
      elif rules == "alpha":
         value = self.purify_set(value, string.ascii_letters)
      elif rules == "alphanumeric":
         value = self.purify_set(value, string.ascii_letters + string.digits)
      elif isinstance(rules, str) and rules.startswith('[') and rules.endswith(']'):
         value = self.purify_set(value, rules[1:-1])
      elif callable(rules):
         value = rules(value)
      else:
         purified = False

      return value, purified

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
      # strip out all encoded tag characters
      for escape_char in HTML_ESCAPE_CHARS.itervalues():
         url = url.replace(escape_char, '')
      
      if '//' not in self.allowed_schemes and url.startswith('//'):
         return '#' # disallow protocol-relative URLs (possible XSS vector)

      parts = url.split(':')
      scheme = ''
      if len(parts) > 1:
         scheme = parts[0]
         if '/' in scheme or '#' in scheme:
            scheme = ''
            url = '#'
         else:
            url = ':'.join(parts[1:])

      if scheme == '':
         return url
      elif scheme.lower() in self.allowed_schemes:
         return '%s:%s' % (scheme, url)
      else:
         return '#'

   def purify_int(self, value):
      try:
         return str(int(value))
      except ValueError:
         return ''

   def purify_set(self, value, allowed_chars):
      if isinstance(value, unicode) or isinstance(allowed_chars, unicode):
         translation_table = dict.fromkeys(map(ord, allowed_chars), None)
         if value.translate(translation_table):
            value = ''
      else:
         if value.translate(self.trans_table, allowed_chars):
            value = ''

      return value
   
   def purify_regex(self, value, regex):
      if regex.match(value):
         return value
      else:
         return ''

def filter_html(html, spec, **kwargs):
   html_filter = HTMLFilter(spec, **kwargs)
   return html_filter.filter(html)


