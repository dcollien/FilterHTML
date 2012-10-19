class HTMLFilter(object):
   def __init__(self, spec):
      self.tag_chars = "abcdefghijklmnopqrstuvwxyz"
      self.attr_chars = "abcdefghijklmnopqrstuvwxyz-"
      self.html = ''
      self.allowed_tags = spec.keys()
      self.safeHTML = ''

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
         return ''

   def filter(self, html):
      self.html = html
      self.chars = self.char_gen()
      self.safeHTML = ''
      while self.next():
         if self.curr_char == '<':
            self.filter_tag()
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

      assert self.curr_char == '>'

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

      return tag_name

   def extract_attribute_name(self):
      attr_name = ''

      if self.curr_char.lower() in self.attr_chars:
         attr_name += self.curr_char.lower()
         while self.next().lower() in self.attr_chars:
            attr_name += self.curr_char.lower()

      return attr_name


   def filter_opening_tag(self):
      self.extract_whitespace()

      tag_name = self.extract_tag_name()
      print 'open', tag_name

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
         while self.next() != '>' and self.curr_char != '':
            pass # skip until tag closed

   def filter_closing_tag(self):
      self.extract_whitespace()

      tag_name = self.extract_tag_name()
      print 'close', tag_name

      if tag_name in self.allowed_tags:
         self.extract_whitespace()
         if self.curr_char == '>':
            self.safeHTML += '</' + tag_name + '>'
            return
      else:
         while self.next() != '>' and self.curr_char != '':
            pass # skip until tag closed

   def filter_attribute(self, tag_name):
      allowed_attributes = self.spec[tag_name].keys()
      
      attribute_name = self.extract_attribute_name()
      print 'attr', attribute_name
      
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
         print self.curr_char
         self.next() # skip invalid characters
         is_allowed = False

      print self.curr_char
      if is_allowed:
         return attribute_name + '=' + value
      else:
         return None


   def filter_value(self, tag_name, attribute_name):
      value = ''
      if self.curr_char == "'" or self.curr_char == '"':
         quote = self.curr_char

         while self.next() != quote:
            if self.curr_char == '':
               break

            value += self.curr_char

         # nom the quote
         self.next()

      if self.spec[tag_name][attribute_name] == "url":
         return quote + self.purify_url(value) + quote

      if attribute_name in self.spec[tag_name] and value in self.spec[tag_name][attribute_name]:
         print 'val', value
         return quote + value + quote
      else:
         return None

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








def make_safe(html, spec):
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
      }
   }

   html = '<div class="btn"><a href="http://localhost:8080">Hello</a> <a href="/foo">World</a><a href="http://www.google.com">Hey</a><script>mwahaha</script></div><x d="e[ =d 8h><A href="javascript:alert(\'xss\');" target="_">Hello</a>'

   print make_safe(html, spec)
