import string

class HTMLFilter(object):
   def __init__(self, spec):
      self.tag_chars = "abcdefghijklmnopqrstuvwxyz"
      self.attr_chars = "abcdefghijklmnopqrstuvwxyz-"
      self.html = ''
      self.allowed_tags = spec.keys()
      self.safeHTML = ''

      self.trans_table = string.maketrans('','')
      self.spec = spec

   def char_gen(self):
      self.curr_char = ''
      for c in self.html:
         self.curr_char = c
         yield c

   def next(self):
      try:
         return self.chars.next()
      except StopIteration:
         self.curr_char = ''
         return ''

   def filter(self, html):
      self.html = html
      self.chars = self.char_gen()
      self.safeHTML = ''
      while self.next():
         if self.curr_char == '<':
            self.filter_tag()
         else:
            if self.curr_char == '>':
               self.safeHTML += '&gt;'
            else:
               self.safeHTML += self.curr_char

      return self.safeHTML


   def filter_tag(self):
      assert self.curr_char == '<'

      if self.next() == '/':
         self.next()
         self.filter_closing_tag()
      else:
         self.filter_opening_tag()

      assert (self.curr_char == '>' or self.curr_char == '')

   def extract_whitespace(self):
      whitespace = ''

      if self.curr_char.isspace():
         whitespace += self.curr_char
         while self.next().isspace():
            whitespace += self.curr_char

      return whitespace

   def extract_tag_name(self):
      tag_name = ''

      if self.curr_char.lower() in self.tag_chars:
         tag_name += self.curr_char.lower()
         while self.next().lower() in self.tag_chars:
            tag_name += self.curr_char.lower()

      while tag_name in self.allowed_tags and isinstance(self.spec[tag_name], str):
         tag_name = self.spec[tag_name] # follow aliases

      return tag_name

   def extract_attribute_name(self):
      attr_name = ''

      if self.curr_char.lower() in self.attr_chars:
         attr_name += self.curr_char.lower()
         while self.next().lower() in self.attr_chars:
            attr_name += self.curr_char.lower()

      return attr_name

   def extract_remaining_tag(self):
      remaining_tag = ''

      if self.curr_char != '>':
         remaining_tag += self.curr_char
         while self.next() != '>' and self.curr_char != '':
            remaining_tag += self.curr_char

      return remaining_tag

   def filter_opening_tag(self):
      self.extract_whitespace()

      tag_name = self.extract_tag_name()

      if tag_name in self.allowed_tags:
         attributes = []
         while self.curr_char != '>' and self.curr_char != '':
            self.extract_whitespace()
            attribute = self.filter_attribute(tag_name)
            if attribute is not None:
               attributes.append(attribute)


         self.safeHTML += '<' + tag_name

         if len(attributes) > 0:
            self.safeHTML += ' ' + ' '.join(attributes)

         self.safeHTML += '>'
      else:
         self.extract_remaining_tag()

   def filter_closing_tag(self):
      self.extract_whitespace()

      tag_name = self.extract_tag_name()

      if tag_name in self.allowed_tags:
         self.extract_whitespace()
         if self.curr_char == '>':
            self.safeHTML += '</' + tag_name + '>'
            return
      else:
         self.extract_remaining_tag()

   def filter_attribute(self, tag_name):
      allowed_attributes = self.spec[tag_name].keys()
      
      attribute_name = self.extract_attribute_name()
      
      whitespace = self.extract_whitespace()

      is_allowed = attribute_name in allowed_attributes

      assignment = ''
      value = None
      if self.curr_char == '=':
         assignment = '='
         
         self.next() # nom the =

         self.extract_whitespace()
         value = self.filter_value(tag_name, attribute_name)
         if value is None:
            is_allowed = False
      
      elif is_allowed and None not in self.spec[tag_name][attribute_name]:
         is_allowed = False

      elif self.curr_char not in self.attr_chars and self.curr_char != '>':
         self.next() # skip invalid characters
         is_allowed = False

      if is_allowed:
         return attribute_name + '=' + value
      else:
         return None


   def filter_value(self, tag_name, attribute_name):
      value = ''
      quote = '"'
      if self.curr_char == "'" or self.curr_char == '"':
         quote = self.curr_char

         while self.next() != quote:
            if self.curr_char == '':
               break

            value += self.curr_char

         # nom the quote
         self.next()



      rules = None
      if attribute_name in self.spec[tag_name]:
         rules = self.spec[tag_name][attribute_name]
      else:
         return None

      if rules == "url":
         value = self.purify_url(value)
      elif rules == "int":
         value = self.purify_int(value)
      elif rules == "alpha":
         value = self.purify_set(value, string.ascii_letters)
      elif rules == "alphanumeric":
         value = self.purify_set(value, string.ascii_letters + string.digits)
      elif isinstance(rules, str) and rules.startswith('[') and rules.endswith(']'):
         value = self.purify_set(value, rules[1:-1])
      elif value not in rules:
         value = ''

      if value == '':
         return None
      else:
         return quote + value + quote

   def purify_url(self, url):
      parts = url.split(':')
      scheme = ''
      if len(parts) > 1:
         if '/' in scheme or '#' in scheme:
            scheme = ''
         else:
            scheme = parts[0]
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
      "b": {},
      "i": {},
      "p": {},

      # alias
      "strong": "b"

   }

   html = '''
<div class="btn">Hello World</div>
<script>alert("bad!")</script>
<unknown>something here</unknown>
<a href="http://www.google.com" onclick="alert('bad!');">Click</a>
<div foo="bah"></div>
<a href="javascript:alert('bad!')">Foo</a>
<div class="foo"></div>
<img src="./foo.png" border="0" width="20" height="20">
<input type="hidden" value="dog42" name="my-dog">
<strong>Hello</strong>
<hr/>
<jun<><FJ = ">"< d09"> <a =<> <junk<>><>
a > 5
b < 3
'''

   print filter_html(html, spec)
demo()
