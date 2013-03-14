import re
import string

TRANS_TABLE = string.maketrans('','')
TAG_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz123456")
ATTR_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz-")

class HTMLFilter(object):
   def __init__(self, spec):
      self.tag_chars = TAG_CHARS
      self.attr_chars = ATTR_CHARS
      self.trans_table = TRANS_TABLE

      self.html = ''
      self.filtered_html = []

      self.allowed_tags = spec.keys()

      # allow global attributes
      if '*' in spec:
         self.global_attrs = spec['*']
      else:
         self.global_attrs = None

      self.spec = spec


   def filter(self, html):
      self.html = html
      self.chars = self.__char_gen()
      self.filtered_html = []
      while self.__next():
         if self.curr_char == '<':
            self.__filter_tag()
         else:
            if self.curr_char == '>':
               self.filtered_html.append('&gt;')
            else:
               self.filtered_html.append(self.curr_char)

      return ''.join(self.filtered_html)


   def __char_gen(self):
      self.curr_char = ''
      for c in self.html:
         self.curr_char = c
         yield c

   def __next(self):
      try:
         return self.chars.next()
      except StopIteration:
         self.curr_char = ''
         return ''

   def __filter_tag(self):
      assert self.curr_char == '<'

      if self.__next() == '/':
         self.__next()
         self.__filter_closing_tag()
      else:
         self.__filter_opening_tag()

      assert (self.curr_char == '>' or self.curr_char == '')

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
      while tag_name in self.allowed_tags and isinstance(self.spec[tag_name], str):
         tag_parts = self.spec[tag_name].split(' ') # follow aliases
         tag_name = tag_parts[0]
         if len(tag_parts) > 1:
            alias_attributes += tag_parts[1:]

      return tag_name, alias_attributes

   def __filter_opening_tag(self):
      self.__extract_whitespace()

      tag_name = self.__extract_tag_name()

      tag_name, attributes = self.__follow_aliases(tag_name)

      if tag_name in self.allowed_tags:
         while self.curr_char != '>' and self.curr_char != '':
            self.__extract_whitespace()
            attribute = self.__filter_attribute(tag_name)
            if attribute is not None:
               attributes.append(attribute)


         self.filtered_html.append('<%s' % (tag_name,))

         if len(attributes) > 0:
            self.filtered_html.append(' ' + ' '.join(attributes))

         self.filtered_html.append('>')
      else:
         self.__extract_remaining_tag()

   def __filter_closing_tag(self):
      self.__extract_whitespace()

      tag_name = self.__extract_tag_name()
      tag_name, attributes = self.__follow_aliases(tag_name)

      if tag_name in self.allowed_tags:
         self.__extract_whitespace()
         if self.curr_char == '>':
            self.filtered_html.append('</%s>' % (tag_name,))
            return
      else:
         self.__extract_remaining_tag()

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
      
      elif is_allowed and None not in self.spec[tag_name][attribute_name]:
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
      if self.global_attrs is not None and attribute_name in self.global_attrs:
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
         if attribute_name == "class":
            candidate_values = value.split(' ')
            allowed_values = [candidate for candidate in candidate_values if candidate in rules]
            value = ' '.join(allowed_values)
         elif attribute_name == "style" and isinstance(rules, dict):
            candidate_values = value.split(';')
            allowed_values = [self.purify_style(style, rules) for style in candidate_values]
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
      if isinstance(rules, re._pattern_type):
         value = self.purify_regex(value, rules)
      elif rules == "url":
         value = self.purify_url(value)
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

      if name in rules:
         style_rules = rules[name]
         value, purified = self.purify_value(value, style_rules)
         if not purified:
            if value not in style_rules:
               return None
      else:
         return None

      return ': '.join([name, value])

   def purify_url(self, url):
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
      elif scheme.lower() in ('http', 'https', 'mailto', 'ftp'):
         return '%s:%s' % (scheme, url)
      else:
         return '#'

   def purify_int(self, value):
      try:
         return str(int(value))
      except ValueError:
         return ''

   def purify_set(self, value, allowed_chars):
      if value.translate(self.trans_table, allowed_chars):
         return ''
      else:
         return value

   def purify_regex(self, value, regex):
      if regex.match(value):
         return value
      else:
         return ''

def filter_html(html, spec):
   html_filter = HTMLFilter(spec)
   return html_filter.filter(html)


