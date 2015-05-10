var FilterHTML = require('../lib/FilterHTML');
module.exports = {};

module.exports.test_no_attrs = function(test) {
   var spec, input_html, expected_html, result;

   spec = {
      'b': {},
      'em': {},
      'br': {},
      'hr': {},
      'span': {}
   };

   input_html =
      '<b>This is a test</b><br>' +
      '<span class="invalid-class">This span tag should be allowed, but its attributes stripped</span>' +
      '<div>This div tag is not allowed, and the tag will be removed</div>' +
      '<span id="invalid-id">This span tag is allowed, but its attributes stripped</span>'
   ;


   expected_html =
      '<b>This is a test</b><br>' +
      '<span>This span tag should be allowed, but its attributes stripped</span>' +
      'This div tag is not allowed, and the tag will be removed' +
      '<span>This span tag is allowed, but its attributes stripped</span>'
   ;

   result = FilterHTML.filter_html(input_html, spec);

   test.equal(expected_html, result);
   test.done();
};

module.exports.test_attribute_types = function(test) {
   var spec, input_html, expected_html, result;
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
   };

   input_html = 
      '<b>This is a test</b><br>' +
      '<ul>' + 
      '   <li type="disc">This is a disc</li>' + 
      '   <li type="circle">This is a circle</li>' + 
      '   <li type="invalid" value="1">This will have the type stripped, but keep its value</li>' + 
      '</ul>' + 
      '<a href="/foo.html" target="_blank">Foo</a><br>' + 
      '<a href="http://www.example.com">Example</a><br>' + 
      '<a href="javascript:invalid();" target="_parent">Stripped</a><br>' + 
      '<img src="image.jpg" height="120" width="240" border="0">'
   ;
      

   expected_html =
      '<b>This is a test</b><br>' +
      '<ul>' +
      '   <li type="disc">This is a disc</li>' +
      '   <li type="circle">This is a circle</li>' +
      '   <li value="1">This will have the type stripped, but keep its value</li>' +
      '</ul>' +
      '<a href="/foo.html" target="_blank">Foo</a><br>' +
      '<a href="http://www.example.com">Example</a><br>' +
      '<a href="#">Stripped</a><br>' +
      '<img src="image.jpg" height="120" width="240">'
   ;

   result = FilterHTML.filter_html(input_html, spec);

   test.equal(expected_html, result);
   test.done();
};

module.exports.test_classes = function(test) {
   var spec, input_html, expected_html, result;

   spec = {
      'span': {
         'class': [
            'pretty',
            'ugly',
            'plain',
         ]
      },
      'b': {},
      'br': {}
   };

   input_html =
      '<b>This is a test</b><br>' + 
      '<span class="pretty">This is pretty</span><br>' + 
      '<span class="pretty pretty">This is just pretty</span><br>' + 
      '<span class="pretty ugly">This is pretty ugly</span><br>' + 
      '<span class="invalid pretty">This is just pretty</span><br>' + 
      '<span class="plain ugly plain ugly invalid">This is plain ugly</span><br>' + 
      '<span class="invalid plain invalid ugly">This is also plain ugly</span><br>' + 
      '<span class="invalid">Stripped</span>' + 
      '<span>This works too</span>'
   ;
   
   expected_html =
      '<b>This is a test</b><br>' + 
      '<span class="pretty">This is pretty</span><br>' + 
      '<span class="pretty">This is just pretty</span><br>' + 
      '<span class="pretty ugly">This is pretty ugly</span><br>' + 
      '<span class="pretty">This is just pretty</span><br>' + 
      '<span class="plain ugly">This is plain ugly</span><br>' + 
      '<span class="plain ugly">This is also plain ugly</span><br>' + 
      '<span>Stripped</span>' + 
      '<span>This works too</span>'
   ;

   result = FilterHTML.filter_html(input_html, spec);

   test.equal(expected_html, result);
   test.done();
};

module.exports.test_styles = function(test) {
   var spec, input_html, expected_html, result;

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
      'br': {}
   };

   input_html =
      '<b>This is a test</b><br>' +
      '<span style="color:red;">red</span><br>' +
      '<span style="color:#fff;">#fff</span><br>' +
      '<span style="color:#f0f0ef;">#f0f0ef</span><br>' +
      '<span style="color:rgb(255, 255, 255);">white</span><br>' +
      '<span style="color:rgba(0, 255, 255, 0.5);">cyan</span><br>' +
      '<span style="color:hsla(40, 20%, 10%, 0.1);">hsla</span><br>' +
      '<span style="color:hsl(40, 20%, 10%);">hsl</span><br>' +
      '<span style="color:invalid;">invalid</span><br>' +
      '<div style="width:32px;height:24px;">div</div>' +
      '<div style="width:32px;height:invalid;">invalid div</div>'
   ;

   expected_html =
      '<b>This is a test</b><br>' +
      '<span style="color:red;">red</span><br>' +
      '<span style="color:#fff;">#fff</span><br>' +
      '<span style="color:#f0f0ef;">#f0f0ef</span><br>' +
      '<span style="color:rgb(255, 255, 255);">white</span><br>' +
      '<span style="color:rgba(0, 255, 255, 0.5);">cyan</span><br>' +
      '<span style="color:hsla(40, 20%, 10%, 0.1);">hsla</span><br>' +
      '<span style="color:hsl(40, 20%, 10%);">hsl</span><br>' +
      '<span>invalid</span><br>' +
      '<div style="width:32px;height:24px;">div</div>' +
      '<div style="width:32px;">invalid div</div>'
   ;

   result = FilterHTML.filter_html(input_html, spec);

   test.equal(expected_html, result);
   test.done();
};

module.exports.test_regex_delegates = function(test) {
   var spec, input_html, expected_html, result;

   var filter_color = function(color) {
      if (['red', 'green', 'blue'].indexOf(color) > 0) {
         return color;
      } else {
         return 'red';
      }
   };

   spec = {
      'span': {
         'style': {
            'color': filter_color,
         }
      },
      'div': {
         'style': {
            'width': /^\d+px$/,
            'height': /^\d+px$/
         }
      },
      'b': {},
      'br': {}
   };

   input_html =
      '<b>This is a test</b><br>' +
      '<span style="color:red;">red</span><br>' +
      '<span style="color:green;">green</span><br>' +
      '<span style="color:blue;">blue</span><br>' +
      '<span style="color:rgb(255, 255, 255);">white</span><br>' +
      '<span style="color:rgb(0, 255, 255);">cyan</span><br>' +
      '<span style="color:hsla(40, 20%, 10%, 0.1);">hsla</span><br>' +
      '<span style="color:invalid;">invalid</span><br>' +
      '<div style="width:32px;height:24px;">div</div>' +
      '<div style="width:32px;height:invalid;">invalid div</div>'
   ;

   expected_html = 
      '<b>This is a test</b><br>' +
      '<span style="color:red;">red</span><br>' +
      '<span style="color:green;">green</span><br>' +
      '<span style="color:blue;">blue</span><br>' +
      '<span style="color:red;">white</span><br>' +
      '<span style="color:red;">cyan</span><br>' +
      '<span style="color:red;">hsla</span><br>' +
      '<span style="color:red;">invalid</span><br>' +
      '<div style="width:32px;height:24px;">div</div>' +
      '<div style="width:32px;">invalid div</div>'
   ;

   result = FilterHTML.filter_html(input_html, spec);

   test.equal(expected_html, result);
   test.done();
};

module.exports.test_wildcard = function(test) {
   var spec, input_html, expected_html, result;
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
   };

   input_html =
      '<b>This is a test</b><br>' +
      '<em id="special-id">allowed special id</em>' +
      '<em id="xxx">allowed id</em>' +
      '<span id="special-id">invalid id</span>' +
      '<span class="invalid-class" id="bar42">This span tag should be allowed, but its attributes stripped</span>' +
      '<div>This div tag is not allowed, and the tag will be removed</div>' +
      '<span style="color:red;" id="foo">This span tag is allowed, but its attributes stripped</span>'
   ;

   expected_html =
      '<b>This is a test</b><br>' +
      '<em id="special-id">allowed special id</em>' +
      '<em id="xxx">allowed id</em>' +
      '<span>invalid id</span>' +
      '<span id="bar42">This span tag should be allowed, but its attributes stripped</span>' +
      'This div tag is not allowed, and the tag will be removed' +
      '<span id="foo">This span tag is allowed, but its attributes stripped</span>'
   ;

   result = FilterHTML.filter_html(input_html, spec);

   test.equal(expected_html, result);
   test.done();
};

module.exports.test_aliases = function(test) {
   var spec, input_html, expected_html, result;

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
   };

   input_html =
      '<b>This is a test</b><br>' + 
      '<center>centered text</center>'
   ;

   expected_html =
      '<strong>This is a test</strong><br>' +
      '<p class="centered">centered text</p>'
   ;

   result = FilterHTML.filter_html(input_html, spec);

   test.equal(expected_html, result);
   test.done();
};

module.exports.test_tag_removal = function(test) {
   var spec, input_html, expected_html, result;

   spec = {
      'span': {},
      'br': {},
   };

   input_html =
      '<span>This is a test</span>' +
      '<script>' +
      '   if (x < 4) {' +
      '      x = 1 << 2;' +
      '      // this should all be gone' +
      '   }' +
      '</script><br>'
   ;

   expected_html =
      '<span>This is a test</span>' +
      '<br>'
   ;

   result = FilterHTML.filter_html(input_html, spec);

   test.equal(expected_html, result, result);

   input_html =
      '<span>This is a test</span>' +
      '<script>' +
      '   if (x < 4) {' +
      '      x = 1 << 2;' +
      '      // this should all be gone' +
      '   }' +
      '</script><br>' +
      '<style>' +
      '   .foo < a {' +
      '      color: red;' +
      '   }' +
      '</style><div>' +
      '   Here\'s a whole lot of stuff to remove' +
      '</div><br><!-- comment -->'
   ;

   expected_html =
      '<span>This is a test</span>' +
      '<br>' +
      '<br>'
   ;

   result = FilterHTML.filter_html(input_html, spec, remove=['script', 'style', 'div']);
   test.equal(expected_html, result, result);
   test.done();
};

module.exports.test_script_conversion = function(test) {
   var spec, input_html, expected_html, result;

   spec = {
      'span': {},
      'br': {},
      'pre': {},
      'script': 'pre'
   };

   input_html =
      '<span>This is a test</span>' +
      '<script>' +
      '   if (x < 4) {' +
      '      x = 1 << 2;' +
      '   }' +
      '</script><br>'
   ;

   expected_html =
      '<span>This is a test</span>' +
      '<pre>' +
      '   if (x &lt; 4) {' +
      '      x = 1 &lt;&lt; 2;' +
      '   }' +
      '</pre><br>'
   ;

   result = FilterHTML.filter_html(input_html, spec);
   test.equal(expected_html, result);
   test.done();
};

// TODO finish off tests as per run_tests.py
