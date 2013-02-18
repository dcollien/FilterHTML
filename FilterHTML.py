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
      self.filtered_html = ''

      self.allowed_tags = spec.keys()

      self.spec = spec


   def filter(self, html):
      self.html = html
      self.chars = self.__char_gen()
      self.filtered_html = ''
      while self.__next():
         if self.curr_char == '<':
            self.__filter_tag()
         else:
            if self.curr_char == '>':
               self.filtered_html += '&gt;'
            else:
               self.filtered_html += self.curr_char

      return self.filtered_html


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
      whitespace = ''

      if self.curr_char.isspace():
         whitespace += self.curr_char
         while self.__next().isspace():
            whitespace += self.curr_char

      return whitespace

   def __extract_tag_name(self):
      tag_name = ''

      if self.curr_char.lower() in self.tag_chars:
         tag_name += self.curr_char.lower()
         while self.__next().lower() in self.tag_chars:
            tag_name += self.curr_char.lower()

      return tag_name

   def __extract_attribute_name(self):
      attr_name = ''

      if self.curr_char.lower() in self.attr_chars:
         attr_name += self.curr_char.lower()
         while self.__next().lower() in self.attr_chars:
            attr_name += self.curr_char.lower()

      return attr_name

   def __extract_remaining_tag(self):
      remaining_tag = ''

      if self.curr_char != '>':
         remaining_tag += self.curr_char
         while self.__next() != '>' and self.curr_char != '':
            remaining_tag += self.curr_char

      return remaining_tag

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


         self.filtered_html += '<' + tag_name

         if len(attributes) > 0:
            self.filtered_html += ' ' + ' '.join(attributes)

         self.filtered_html += '>'
      else:
         self.__extract_remaining_tag()

   def __filter_closing_tag(self):
      self.__extract_whitespace()

      tag_name = self.__extract_tag_name()
      tag_name, attributes = self.__follow_aliases(tag_name)

      if tag_name in self.allowed_tags:
         self.__extract_whitespace()
         if self.curr_char == '>':
            self.filtered_html += '</' + tag_name + '>'
            return
      else:
         self.__extract_remaining_tag()

   def __filter_attribute(self, tag_name):
      allowed_attributes = self.spec[tag_name].keys()
      
      attribute_name = self.__extract_attribute_name()
      
      whitespace = self.__extract_whitespace()

      is_allowed = attribute_name in allowed_attributes

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
         return attribute_name + '=' + value
      else:
         return None


   def __filter_value(self, tag_name, attribute_name):
      value = ''
      quote = '"'
      if self.curr_char == "'" or self.curr_char == '"':
         quote = self.curr_char

         while self.__next() != quote:
            if self.curr_char == '':
               break

            value += self.curr_char

         # nom the quote
         self.__next()



      rules = None
      if attribute_name in self.spec[tag_name]:
         rules = self.spec[tag_name][attribute_name]
      else:
         return None

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
      elif attribute_name == "class":
         candidate_values = value.split(' ')
         allowed_values = []
         for candidate in candidate_values:
            if candidate in rules:
               allowed_values.append(candidate)
         value = ' '.join(allowed_values)
      elif value not in rules:
         value = ''
      
      if value is None or value == '':
         return None
      else:
         return quote + value + quote

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
         return scheme + ':' + url
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


def demo():
   spec = {
      "div": {
         "class": [
            "btn",
            "container"
         ]
      },
      "a": {
         "href": "url",
         "target": [
            "_blank"
         ]
      },
      "img": {
         "src": "url",
         "border": "int",
         "width": "int",
         "height": "int"
      },
      "input": {
         "type": "alpha",
         "name": "[abcdefghijklmnopqrstuvwxyz-]",
         "value": "alphanumeric"
      },
      "hr": {},
      "br": {},
      "strong": {},
      "i": {
         "class": re.compile('^icon-[a-z0-9_]+$')
      },
      "p": {
         "class": [
            "centered"
         ]
      },

      # alias
      "b": "strong",
      "center": "p class=\"centered\""

   }

   html = '''
<div class="btn">Hello World</div>
<script>alert("bad!")</script>
<unknown>something here</unknown>
<a href="http://www.google.com" onclick="alert('bad!');">Click</a>
<div foo="bah"></div>
<a href="javascript:alert('bad!')">Foo</a>
<div class="foo"></div><a href="#:x"></a>
<img src="./foo.png" border="0" width="20" height="20">
<input type="hidden" value="dog42" name="my-dog">
<input type="not allowed" value="xxx" name="_+_">
<b>Hello</b>
<p style="display:none">Text</p>
<i class="icon-hello"></i>
<i class="icon-"></i>
<i class="icon->"></i>
<center>This is Centered</center>
<hr/>
<jun<><FJ = ">"< d09"> <a =<> <junk<>><>
a > 5
b < 3
'''

   expected = '''
<div class="btn">Hello World</div>
alert("bad!")
something here
<a href="http://www.google.com">Click</a>
<div></div>
<a href="#">Foo</a>
<div></div><a href="#"></a>
<img src="./foo.png" border="0" width="20" height="20">
<input type="hidden" value="dog42" name="my-dog">
<input value="xxx">
<strong>Hello</strong>
<p>Text</p>
<i class="icon-hello"></i>
<i></i>
<i></i>
<p class="centered">This is Centered</p>
<hr>
" <a> &gt;
a &gt; 5
b
'''
   
   filtered = filter_html(html, spec)

   print filtered
   assert filtered.strip() == expected.strip()

