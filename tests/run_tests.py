from __future__ import print_function

import unittest, re

import FilterHTML

def print_diff(expected_html, result):
   import difflib

   d = difflib.Differ()
   print(''.join(d.compare(expected_html, result)))

class TestFiltering(unittest.TestCase):
   def test_escape_data(self):
      input_html = "-&gt;"
      expected_html = "-&gt;"

      result = FilterHTML.filter_html(input_html, {})

      self.assertEqual(expected_html, result)

   def test_unquoted_urls(self):
      spec = {
         'a': {
            'href': 'url',
            'checked': 'boolean'
         }
      }

      input_html = "<a href=http://www.example.com></a>"
      expected_html = "<a href=\"http://www.example.com\"></a>"

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

      input_html = "<a href= checked></a>"
      expected_html = "<a href=\"#\" checked></a>"

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_empty_urls(self):
      spec = {
         'a': {
            'href': 'url|empty'
         }
      }

      input_html = "<a href=\"   \"></a>"
      expected_html = "<a href=\"\"></a>"

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

      input_html = "<a href=\"\"></a>"
      expected_html = "<a href=\"\"></a>"

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

      input_html = "<a href=\"javascript://invalid\"></a>"
      expected_html = "<a href=\"\"></a>"

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_boolean_attrs(self):
      spec = {
         'input': {
            'type': 'alpha',
            'checked': 'boolean'
         }
      }

      input_html = "<input type=\"checkbox\" checked>"
      expected_html = "<input type=\"checkbox\" checked>"

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

      input_html = "<input type=checkbox checked>"
      expected_html = "<input type=\"checkbox\" checked>"

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   
      input_html = "<input type= checked>"
      expected_html = "<input checked>"

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_text_attrs(self):
      spec = {
         'img': {
            'src': 'url',
            'alt': 'alphanumeric|empty'
         }
      }

      input_html = "<img src=\"\" alt=\"\">"
      expected_html = "<img src=\"#\" alt=\"\">"

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

      spec = {
         'img': {
            'src': 'url',
            'alt': 'text',
         }
      }
      input_html = "<img src=\"\" alt='\"hello!\" <THIS> & is encoded &quot; &;'>"
      expected_html = "<img src=\"#\" alt='&quot;hello!&quot; &lt;THIS&gt; &amp; is encoded &quot; &amp;&semi;'>"

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_no_attrs(self):
      spec = {
         'b': {},
         'em': {},
         'br': {},
         'hr': {},
         'span': {}
      }

      input_html = """
      <b>This is a test</b><br>
      <span class="invalid-class">This span tag should be allowed, but its attributes stripped</span>
      <div>This div tag is not allowed, and the tag will be removed</div>
      <span id="invalid-id">This span tag is allowed, but its attributes stripped</span>
      """

      expected_html = """
      <b>This is a test</b><br>
      <span>This span tag should be allowed, but its attributes stripped</span>
      This div tag is not allowed, and the tag will be removed
      <span>This span tag is allowed, but its attributes stripped</span>
      """

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_attribute_types(self):
      spec = {
         'a': {
            'href': 'url',
            'target': [
               '_blank',
               '_self',
            ]
         },
         'img': {
            'src': 'url',
            'height': 'measurement',
            'width': 'measurement',
         },
         'b': {},
         'br': {},
         'ul': {},
         'li': {
            'type': [
               '1',
               'A',
               'a',
               'I',
               'i',
               'disc',
               'square',
               'circle',
            ],
            'value': 'int'
         }
      }

      input_html = """
      <b>This is a test</b><br>
      <ul>
         <li type="disc">This is a disc</li>
         <li type="circle">This is a circle</li>
         <li type="invalid" value="1">This will have the type stripped, but keep its value</li>
      </ul>
      <a href="/foo.html" target="_blank">Foo</a><br>
      <a href="http://www.example.com">Example</a><br>
      <a href="javascript:invalid();" target="_parent">Stripped</a><br>
      <img src="image.jpg" height="120" width="240" border="0">
      """

      expected_html = """
      <b>This is a test</b><br>
      <ul>
         <li type="disc">This is a disc</li>
         <li type="circle">This is a circle</li>
         <li value="1">This will have the type stripped, but keep its value</li>
      </ul>
      <a href="/foo.html" target="_blank">Foo</a><br>
      <a href="http://www.example.com">Example</a><br>
      <a href="#">Stripped</a><br>
      <img src="image.jpg" height="120" width="240">
      """

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_classes(self):
      spec = {
         'span': {
            'class': [
               'pretty',
               'ugly',
               'plain',
            ]
         },
         'b': {},
         'br': {},
      }

      input_html = """
      <b>This is a test</b><br>
      <span class="pretty">This is pretty</span><br>
      <span class="pretty pretty">This is just pretty</span><br>
      <span class="pretty ugly">This is pretty ugly</span><br>
      <span class="invalid pretty">This is just pretty</span><br>
      <span class="plain ugly plain ugly invalid">This is plain ugly</span><br>
      <span class="invalid plain invalid ugly">This is also plain ugly</span><br>
      <span class="invalid">Stripped</span>
      <span>This works too</span>
      """

      expected_html = """
      <b>This is a test</b><br>
      <span class="pretty">This is pretty</span><br>
      <span class="pretty">This is just pretty</span><br>
      <span class="pretty ugly">This is pretty ugly</span><br>
      <span class="pretty">This is just pretty</span><br>
      <span class="plain ugly">This is plain ugly</span><br>
      <span class="plain ugly">This is also plain ugly</span><br>
      <span>Stripped</span>
      <span>This works too</span>
      """

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_styles(self):
      spec = {
         'span': {
            'style': {
               'color': 'color',
            }
         },
         'div': {
            'style': {
               'width': 'measurement',
               'height': 'measurement'
            }
         },
         'b': {},
         'br': {},
      }

      input_html = """
      <b>This is a test</b><br>
      <span style="color:red;">red</span><br>
      <span style="color:#fff;">#fff</span><br>
      <span style="color:#f0f0ef;">#f0f0ef</span><br>
      <span style="color:rgb(255, 255, 255);">white</span><br>
      <span style="color:rgba(0, 255, 255, 0.5);">cyan</span><br>
      <span style="color:hsla(40, 20%, 10%, 0.1);">hsla</span><br>
      <span style="color:hsl(40, 20%, 10%);">hsl</span><br>
      <span style="color:invalid;">invalid</span><br>
      <div style="width:32px;height:24px;">div</div>
      <div style="width:32px;height:invalid;">invalid div</div>
      """

      expected_html = """
      <b>This is a test</b><br>
      <span style="color:red;">red</span><br>
      <span style="color:#fff;">#fff</span><br>
      <span style="color:#f0f0ef;">#f0f0ef</span><br>
      <span style="color:rgb(255, 255, 255);">white</span><br>
      <span style="color:rgba(0, 255, 255, 0.5);">cyan</span><br>
      <span style="color:hsla(40, 20%, 10%, 0.1);">hsla</span><br>
      <span style="color:hsl(40, 20%, 10%);">hsl</span><br>
      <span>invalid</span><br>
      <div style="width:32px;height:24px;">div</div>
      <div style="width:32px;">invalid div</div>
      """

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_regex_delegates(self):

      def filter_color(color):
         if color in ['red', 'green', 'blue']:
            return color
         else:
            return 'red'

      spec = {
         'span': {
            'style': {
               'color': filter_color,
            }
         },
         'div': {
            'style': {
               'width': re.compile(r'^\d+px$'),
               'height': re.compile(r'^\d+px$')
            }
         },
         'b': {},
         'br': {},
      }

      input_html = """
      <b>This is a test</b><br>
      <span style="color:red;">red</span><br>
      <span style="color:green;">green</span><br>
      <span style="color:blue;">blue</span><br>
      <span style="color:rgb(255, 255, 255);">white</span><br>
      <span style="color:rgb(0, 255, 255);">cyan</span><br>
      <span style="color:hsla(40, 20%, 10%, 0.1);">hsla</span><br>
      <span style="color:invalid;">invalid</span><br>
      <div style="width:32px;height:24px;">div</div>
      <div style="width:32px;height:invalid;">invalid div</div>
      """

      expected_html = """
      <b>This is a test</b><br>
      <span style="color:red;">red</span><br>
      <span style="color:green;">green</span><br>
      <span style="color:blue;">blue</span><br>
      <span style="color:red;">white</span><br>
      <span style="color:red;">cyan</span><br>
      <span style="color:red;">hsla</span><br>
      <span style="color:red;">invalid</span><br>
      <div style="width:32px;height:24px;">div</div>
      <div style="width:32px;">invalid div</div>
      """

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_wildcard(self):
      spec = {
         'b': {},
         'em': {
            'id': [
               'special-id'
            ]
         },
         'br': {},
         'hr': {},
         'span': {},
         '*': {
            'id': 'alphanumeric'
         }
      }

      input_html = """
      <b>This is a test</b><br>
      <em id="special-id">allowed special id</em>
      <em id="xxx">allowed id</em>
      <span id="special-id">invalid id</span>
      <span class="invalid-class" id="bar42">This span tag should be allowed, but its attributes stripped</span>
      <div>This div tag is not allowed, and the tag will be removed</div>
      <span style="color:red;" id="foo">This span tag is allowed, but its attributes stripped</span>
      """

      expected_html = """
      <b>This is a test</b><br>
      <em id="special-id">allowed special id</em>
      <em id="xxx">allowed id</em>
      <span>invalid id</span>
      <span id="bar42">This span tag should be allowed, but its attributes stripped</span>
      This div tag is not allowed, and the tag will be removed
      <span id="foo">This span tag is allowed, but its attributes stripped</span>
      """

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_aliases(self):
      spec = {
         'p': {
            'class': [
               'centered'
            ]
         },
         'strong': {},
         'br': {},
         'b': 'strong',
         'center': 'p class="centered"'
      }

      input_html = """
      <b>This is a test</b><br>
      <center>centered text</center>
      """

      expected_html = """
      <strong>This is a test</strong><br>
      <p class="centered">centered text</p>
      """

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_tag_removal(self):
      spec = {
         'span': {},
         'br': {},
      }

      input_html = """
      <span>This is a test</span>
      <script>
         if (x < 4) {
            x = 1 << 2;
            // this should all be gone
         }
      </script><br>
      """

      expected_html = """
      <span>This is a test</span>
      <br>
      """

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)


      input_html = """
      <span>This is a test</span>
      <script>
         if (x < 4) {
            x = 1 << 2;
            // this should all be gone
         }
      </script><br>
      <style>
         .foo < a {
            color: red;
         }
      </style><div>
         Here's a whole lot of stuff to remove
      </div><br><!-- comment -->
      """

      expected_html = """
      <span>This is a test</span>
      <br>
      <br>
      """


      result = FilterHTML.filter_html(input_html, spec, remove=['script', 'style', 'div'])
      self.assertEqual(expected_html, result)

   def test_script_conversion(self):
      spec = {
         'span': {},
         'br': {},
         'pre': {},
         'script': 'pre'
      }

      input_html = """
      <span>This is a test</span>
      <script>
         if (x < 4) {
            x = 1 << 2;
         }
      </script><br>
      """

      expected_html = """
      <span>This is a test</span>
      <pre>
         if (x &lt; 4) {
            x = 1 &lt;&lt; 2&semi;
         }
      </pre><br>
      """

      result = FilterHTML.filter_html(input_html, spec)
      self.assertEqual(expected_html, result)

   def test_script_noeffect(self):
      spec = {
         'span': {},
         'br': {},
         'pre': {},
         'script': True
      }

      input_html = """
      <span>This is a test</span>
      <script>
         if (x < 4) {
            x = 1 << 2;
         }
      </script><br>
      """

      result = FilterHTML.filter_html(input_html, spec)
      self.assertEqual(input_html, result)


   def test_invalid_html(self):
      spec = {
         'b': {},
         'br': {},
         'span': {
            'id': 'alphanumeric'
         },
      }

      with self.assertRaises(FilterHTML.TagMismatchError):
         result = FilterHTML.filter_html("<b>test<br>", spec)

      with self.assertRaises(FilterHTML.TagMismatchError):
         result = FilterHTML.filter_html("<br>test</b>", spec)

      with self.assertRaises(FilterHTML.TagMismatchError):
         result = FilterHTML.filter_html("<span><br>test</b>", spec)

      with self.assertRaises(FilterHTML.HTMLSyntaxError):
         result = FilterHTML.filter_html("<br>test<span id=\"foo", spec)

      result = FilterHTML.filter_html(u'<span id="\u2713">check</span>', spec)
      self.assertEqual('<span>check</span>', result)

   def test_url(self):
      spec = {
         'a': {
            'href': 'url'
         }
      }

      input_html = """
      <a href="javascript:alert('XSS');"></a>
      <a href="javascript:alert('XSS')"></a>
      <a href=javascript:alert('XSS')></a>
      <a href=JaVaScRiPt:alert('XSS')></a>
      <a href="JaVaScRiPt:alert('XSS')"></a>
      <a href=javascript:alert("XSS")></a>
      <a href="javascript:alert(\"XSS\")"></a>
      <a href=`javascript:alert("XSS 'XSS'")`></a>
      <a href=javascript:alert(String.fromCharCode(88,83,83))></a>
      <a href="javascript:alert(String.fromCharCode(88,83,83))"></a>
      <a href=# onmouseover="alert('xxs')"></a>
      <a href= onmouseover="alert('xxs')"></a>
      <a href=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;
      &#39;&#88;&#83;&#83;&#39;&#41;></a>
      <a href="&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;
      &#39;&#88;&#83;&#83;&#39;&#41;"></a>
      <a href=&#0000106&#0000097&#0000118&#0000097&#0000115&#0000099&#0000114&#0000105&#0000112&#0000116&#0000058&#0000097&
      #0000108&#0000101&#0000114&#0000116&#0000040&#0000039&#0000088&#0000083&#0000083&#0000039&#0000041></a>
      <a href="&#0000106&#0000097&#0000118&#0000097&#0000115&#0000099&#0000114&#0000105&#0000112&#0000116&#0000058&#0000097&
      #0000108&#0000101&#0000114&#0000116&#0000040&#0000039&#0000088&#0000083&#0000083&#0000039&#0000041"></a>
      <a href=&#x6A&#x61&#x76&#x61&#x73&#x63&#x72&#x69&#x70&#x74&#x3A&#x61&#x6C&#x65&#x72&#x74&#x28&#x27&#x58&#x53&#x53&#x27&#x29></a>
      <a href="&#x6A&#x61&#x76&#x61&#x73&#x63&#x72&#x69&#x70&#x74&#x3A&#x61&#x6C&#x65&#x72&#x74&#x28&#x27&#x58&#x53&#x53&#x27&#x29"></a>
      <a href="jav   ascript:alert('XSS');"></a>
      <a href="jav&#x09;ascript:alert('XSS');"></a>
      <a href="javascript&#58;alert('XSS');"></a>
      <a href="javascript&#58alert('XSS');"></a>
      <a href="jav&#x0A;ascript:alert('XSS');"></a>
      <a href="jav&#x0D;ascript:alert('XSS');"></a>
      """

      expected_html = """
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      <a href="#"></a>
      """

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_text_filtering(self):
      spec = {
         'a': {
            'href': 'url'
         },
         'br': {}
      }

      # very basic url autolinking
      URLIZE_RE = '(%s)' % '|'.join([
         r'<(?:f|ht)tps?://[^>]*>',
         r'\b(?:f|ht)tps?://[^)<>\s]+[^.,)<>\s]',
      ])

      def urlize(text, stack):
         is_inside_a_tag = False
         for tag in stack:
            tag_name, attributes = tag
            if tag_name == 'a':
               is_inside_a_tag = True
               break

         if is_inside_a_tag:
            # already linked
            return text
         else:
            return re.sub(URLIZE_RE, r'<a href="\1" class="invalid">\1</a>', text)

      input_html = """
      <a href="http://www.example.com">example</a><br>
      <a href="http://www.example.com">http://www.example.com</a><br>
      http://www.example.com<br>
      """

      expected_html = """
      <a href="http://www.example.com">example</a><br>
      <a href="http://www.example.com">http://www.example.com</a><br>
      <a href="http://www.example.com">http://www.example.com</a><br>
      """

      result = FilterHTML.filter_html(input_html, spec, text_filter=urlize)

      self.assertEqual(expected_html, result)

   def test_spec_delegate(self):
      def allow_inside_span(tag_name, tag_stack):
         is_inside_span = False
         is_inside_div = False
         for tag in tag_stack:
            tag_name, attributes = tag
            if tag_name == 'span':
               is_inside_span = True
            elif tag_name == 'div':
               is_inside_div = True

         if is_inside_span:
            return {
               'href': 'url'
            }
         elif is_inside_div:
            return False # delete
         else:
            return None

      spec = {
         'span': {},
         'div': {},
         'a': allow_inside_span
      }

      input_html = """
      <a href="invalid.html">Hello</a>
      <span><a href="valid.html">Valid</a></span>
      <div><a href="removed.html">Removed</a></div>
      """

      expected_html = """
      Hello
      <span><a href="valid.html">Valid</a></span>
      <div></div>
      """

      result = FilterHTML.filter_html(input_html, spec)
      self.assertEqual(expected_html, result)

   def test_attribute_wildcard(self):
      spec = {
         'span': {'*': ['just-an-id', 'true', 'something']},
         'div': {}
      }

      input_html = """
      <span id="just-an-id">This span tag is allowed, its attributes are wildcarded, its attribute values allowed.</span>
      <span data-anything="true" data-another-attr="something">This span tag is allowed, its attributes are wildcarded, its attribute values allowed.</span>
      <span data-attr-three="unallowed_value">This span tag is allowed, but its attribute value not</span>
      <div data-anything="true">This div tag is allowed, but its attribtues stripped</div>
      """

      expected_html = """
      <span id="just-an-id">This span tag is allowed, its attributes are wildcarded, its attribute values allowed.</span>
      <span data-anything="true" data-another-attr="something">This span tag is allowed, its attributes are wildcarded, its attribute values allowed.</span>
      <span>This span tag is allowed, but its attribute value not</span>
      <div>This div tag is allowed, but its attribtues stripped</div>
      """

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_attribute_value_wildcard(self):
      spec = {
         'span': {'id': '*'},
         'div': {}
      }

      input_html = """
      <span id="just-an-id">This span tag is allowed, id-attribute has wildcard.</span>
      <span id="true">This span tag is allowed, id-attribute has wildcard.</span>
      <span id="fooBar1234">This span tag is allowed, id-attribute has wildcard.</span>
      <span width="100px">This span tag is allowed, but its width-attribute stripped</span>
      <div id="remove-me">This div tag is allowed, but its attribtues stripped</div>
      """

      expected_html = """
      <span id="just-an-id">This span tag is allowed, id-attribute has wildcard.</span>
      <span id="true">This span tag is allowed, id-attribute has wildcard.</span>
      <span id="fooBar1234">This span tag is allowed, id-attribute has wildcard.</span>
      <span>This span tag is allowed, but its width-attribute stripped</span>
      <div>This div tag is allowed, but its attribtues stripped</div>
      """

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)

   def test_regex_attribute_name_delegates(self):

      spec = {
         'span': {
            re.compile(r'^data-attr[\w-]+$'): ['true', 'false'],
            re.compile(r'^data-test[\w-]+$'): ['a', 'b'],
            'id': ['test']
         },
      }

      input_html = """
      <span data-attr-one="true">Span content</span>
      <span data-attr-two="true" data-attribute-three="false">Span content</span>
      <span id="remove-me" data-test-one="a">Span content</span>
      <span id="test" data-test="remove-me">Span content</span>
      <span width="100px">Span content</span>
      <div data-foobar="false">Tag and Attribute allowed</div>
      """

      expected_html = """
      <span data-attr-one="true">Span content</span>
      <span data-attr-two="true" data-attribute-three="false">Span content</span>
      <span data-test-one="a">Span content</span>
      <span id="test">Span content</span>
      <span>Span content</span>
      Tag and Attribute allowed
      """

      result = FilterHTML.filter_html(input_html, spec)

      self.assertEqual(expected_html, result)


if __name__ == '__main__':
    unittest.main()
