var FilterHTML = (function() {

   var TAG_REGEX = /^[a-z1-6]$/;
   var ATTR_REGEX = /^[a-z\-]$/;
   var UNQUOTED_INVALID_REGEX = /^[\"'`=<>]$/;
   var WHITESPACE_REGEX = /^\s$/;
   var UNICODE_REGEX = /^.*&#.*$/;
   var CSS_ESCAPE = /^.*\\[0-9A-Fa-f].*$/;
   var INVALID_ATTRIBUTE_REPLACEMENTS = {
      'url': '#',
      'url|empty': ''
   };
   var UNSAFE_URL_CHARS = {
      " ": "%20",
      "%": "%25",
      ">": "%3E",
      "<": "%3C",
      "[": "%5B",
      "]": "%5D",
      "{": "%7B",
      "}": "%7D",
      "|": "%7C",
      "\\": "%5C",
      "^": "%5E"
   };
   var VOID_ELEMENTS = [
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
   ];
   var HTML_ESCAPE_CHARS = {
      '>': '&gt;',
      '<': '&lt;',
      '&': '&amp;',
      ';': '&semi;'
   };
   var HTML_ESCAPE_QUOTES = {
      '"': '&quot;',
      '\"': '&apos;'
   };

   var URL_ENCODING_MATCH = /(\%[0-9a-fA-F]{2})/g;
   var ENTITY_MATCH = /(\&[\#\d\w]+;)/g;

   // predefined HTML colors
   var HTML_COLORS = [
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
   ];

   // different HTML color formats
   var HEX_MATCH = /^#([0-9A-Fa-f]{3}){1,2}$/;

   var RGB_MATCH = /^rgb\(\s*\d+%?\s*,\s*\d+%?\s*,\s*\d+%?\s*\)$/;

   var RGBA_MATCH = /^rgba\(\s*\d+%?\s*,\s*\d+%?\s*,\s*\d+%?\s*,\s*(\d+\.)?\d+\s*\)$/;

   var HSL_MATCH = /^hsl\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*\)$/;

   var HSLA_MATCH = /^hsla\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*,\s*(\d+\.)?\d+\s*\)$/;

   var MEASUREMENT_MATCH = /^(-?\d+(px|cm|pt|em|ex|pc|mm|in)?|\d+%)$/;

   var HTMLFilter = function(spec, allowed_schemes, text_filter, remove) {
      var i;

      this.html = '';
      this.filtered_html = '';
      this.spec = spec;
      this.global_attrs = spec['*'];
      this.state = 'data';
      this.tag_removing = null;

      if (!this.global_attrs) {
         this.global_attrs = [];
      }
      
      if (allowed_schemes) {
         this.allowed_schemes = allowed_schemes;
      } else {
         this.allowed_schemes = ['http', 'https', 'mailto', 'ftp'];
      }

      if (text_filter) {
         this.text_filter = text_filter;
      } else {
         this.text_filter = null;
      }

      if (remove) {
         this.removals = remove;
      } else {
         // by default scripts and styles are purged, if they don't exist in the spec
         this.removals = [];
         if (!this.spec['script']) {
           this.removals.push('script');
         }
         if (!this.spec['style']) {
           this.removals.push('style');
         }
      }

      this.remove_scripts = false;
      for (i = 0; i !== this.removals.length; ++i) {
         if (this.removals[i] === 'script') {
            this.remove_scripts = true;
            break;
         }
      }
   };
   
   HTMLFilter.prototype.filter = function(html) {
      var tags, i, tag_text, tag_output, text_chars;
      var is_script_processed, is_script_escaped;

      this.row = 0;
      this.line = 0;

      this.html = html;
      this.filtered_html = '';
      this.curr_index = 0;
      this.tag_stack = [];

      is_script_processed = !this.remove_scripts;
      is_script_escaped = this.spec['script'] && (typeof this.spec['script'] === 'string');

      text_chars = '';
      while (this.next()) {
         if (this.curr_char === '<') {
            if (this.state === 'script-data' && !is_script_escaped) {
               tag_text = '' + text_chars;
            } else {
               tag_text = this.filter_text(text_chars);
            }

            tag_output = this.filter_tag();

            if (this.state === 'script-data-less-than-sign') {
               if (is_script_processed) {
                  text_chars += '<';
                  text_chars += this.curr_char;
               }

               this.state = 'script-data';
            } else {
               this.filtered_html += tag_text;
               text_chars = '';
               this.filtered_html += tag_output;
            }
         } else {
            if (this.state === 'script-data' && !is_script_processed) {
               // pass
            } else if (this.state === 'skip-data') {
               // pass
            } else {
               text_chars += this.curr_char;
            }
         }
      }

      this.filtered_html += this.filter_text(text_chars);

      if (this.tag_stack.length !== 0) {
         tags = [];
         for (i = 0; i !== this.tag_stack.length; ++i) {
            tags.push(this.tag_stack[i][0]);
         }
         throw {
            name: 'Tag Mismatch Error',
            message: 'Tags not closed: ' + tags.join(', ')
         };
      }

      return this.filtered_html;
   };

   HTMLFilter.prototype.get_tag_spec = function(tag_name) {
      var tag_spec = this.spec[tag_name];

      if (typeof(tag_spec) === 'function') {
         tag_spec = tag_spec(tag_name, this.tag_stack);
      }

      if (!tag_spec) {
         tag_spec = null;
      }

      return tag_spec;
   };

   HTMLFilter.prototype.escape_data = function(data_char, include_quotes) {
      if (HTML_ESCAPE_CHARS[data_char]) {
         return HTML_ESCAPE_CHARS[data_char];
      } else if (include_quotes && HTML_ESCAPE_QUOTES[data_char]) {
         return HTML_ESCAPE_QUOTES[data_char];
      } else {
         return data_char;
      }
   };

   HTMLFilter.prototype.filter_text = function(text_chars) {
      var filtered_html, filtered_text;
      
      filtered_html = '';

      if (this.text_filter) {
         filtered_text = this.text_filter(text_chars, this.tag_stack);
         filtered_text = filter_html(filtered_text, this.spec, this.allowed_schemes, null, this.removals);
         filtered_html += filtered_text;
      } else {
         filtered_html += this.purify_text(text_chars, false);
      }

      return filtered_html;
   };

   HTMLFilter.prototype.next = function() {
      this.curr_char = this.html.charAt(this.curr_index);
      this.curr_index++;
      
      this.row++;
      if (this.curr_char === '\n') {
         this.line++;
         this.row = 0;
      }

      return this.curr_char;
   };

   HTMLFilter.prototype.filter_tag = function() {
      var tag_output;
      
      tag_output = '';
      
      this.next();
      if (this.curr_char === '/') {
         this.next();
         tag_output = this.filter_closing_tag();
      } else if (this.curr_char === '!' && this.state !== 'script-data') {
         this.extract_remaining_tag();
      } else {
         if (this.state === 'script-data') {
            this.state = 'script-data-less-than-sign';
         } else {
            tag_output = this.filter_opening_tag();
         }
      }

      return tag_output;
   };

   HTMLFilter.prototype.extract_whitespace = function() {
      var whitespace = '';

      if (WHITESPACE_REGEX.test(this.curr_char)) {
         whitespace += this.curr_char;
         while (WHITESPACE_REGEX.test(this.next())) {
            whitespace += this.curr_char;
         }
      }

      return whitespace;
   };

   HTMLFilter.prototype.extract_tag_name = function() {
      var tag_name = '';

      if (TAG_REGEX.test(this.curr_char.toLowerCase())) {
         tag_name += this.curr_char.toLowerCase();
         while (TAG_REGEX.test(this.next().toLowerCase())) {
            tag_name += this.curr_char.toLowerCase();
         }
      }

      return tag_name;
   };


   HTMLFilter.prototype.extract_attribute_name = function() {
      var attr_name = '';

      if (ATTR_REGEX.test(this.curr_char.toLowerCase())) {
         attr_name += this.curr_char.toLowerCase();
         while (ATTR_REGEX.test(this.next().toLowerCase())) {
            attr_name += this.curr_char.toLowerCase();
         }
      }

      return attr_name;
   };

   HTMLFilter.prototype.extract_remaining_tag = function() {
      var remaining_tag = '';

      if (this.curr_char !== '>') {
         remaining_tag += this.curr_char;
         while (this.next() !== '>' && this.curr_char !== '') {
            remaining_tag += this.curr_char;
         }
      }
      return remaining_tag;
   };

   HTMLFilter.prototype.follow_aliases = function(tag_name) {
      var tag_parts, alias_attributes;

      alias_attributes = [];

      while (this.spec[tag_name] && (typeof this.spec[tag_name] === 'string')) {
         tag_parts = this.spec[tag_name].split(' '); // follow aliases
         tag_name = tag_parts[0];
         if (tag_parts.length > 1) {
            alias_attributes = alias_attributes.concat(tag_parts.slice(1));
         }
      }

      return [tag_name, alias_attributes];
   };

   HTMLFilter.prototype.filter_opening_tag = function() {
      var tag_output, i, is_void, tag_name, tag_spec, tag_parts, attributes, attribute, is_recognised_tag;
      
      tag_output = '';

      this.extract_whitespace();

      tag_name = this.extract_tag_name();
      tag_spec = this.get_tag_spec(tag_name);

      if (tag_name === 'script') {
         this.state = 'script-data';
      } else if (tag_spec === false) {
         this.tag_removing = tag_name;
         this.state = 'skip-data';
      } else {
         for (i = 0; i !== this.removals.length; ++i) {
            if (this.removals[i] === tag_name) {
               this.tag_removing = tag_name;
               this.state = 'skip-data';
               break;
            }
         }
      }

      tag_parts = this.follow_aliases(tag_name);
      tag_name = tag_parts[0];
      attributes = tag_parts[1];

      is_recognised_tag = tag_spec !== null && tag_spec !== false;

      if (is_recognised_tag) {
         while (this.curr_char !== '>' && this.curr_char !== '') {
            this.extract_whitespace();
            attribute = this.filter_attribute(tag_name);
            if (attribute) {
               attributes.push(attribute);
            }
         }

         tag_output += '<' + tag_name;

         if (attributes.length > 0) {
            tag_output += ' ' + attributes.join(' ');
         }

         tag_output += '>';

         is_void = false;
         for (i = 0; i !== VOID_ELEMENTS.length; ++i) {
            if (tag_name === VOID_ELEMENTS[i]) {
               is_void = true;
               break;
            }
         }
         if (!is_void) {
            this.tag_stack.push([tag_name, attributes]);
         }
      } else {
         this.extract_remaining_tag();
      }

      return tag_output;
   };

   HTMLFilter.prototype.filter_closing_tag = function() {
      var tag_output, i, is_void, tag_name, tag_spec, tag_parts, opening_tag_name, is_recognised_tag;

      tag_output = '';

      this.extract_whitespace();

      tag_name = this.extract_tag_name();

      is_void = false;
      for (i = 0; i !== VOID_ELEMENTS.length; ++i) {
         if (tag_name === VOID_ELEMENTS[i]) {
            is_void = true;
            break;
         }
      }

      if (tag_name === 'script' && this.state === 'script-data') {
         this.state = 'data';
      } else if (tag_name === this.tag_removing && this.state === 'skip-data') {
         this.state = 'data';
         this.tag_removing = null;
      }

      tag_parts = this.follow_aliases(tag_name);
      tag_name = tag_parts[0];
      tag_spec = this.get_tag_spec(tag_name);

      is_recognised_tag = tag_spec !== null && tag_spec !== false;

      if (is_recognised_tag && !is_void) {
         this.extract_whitespace();
         if (this.curr_char === '>') {
            tag_output += '</' + tag_name + '>';

            if (this.tag_stack.length === 0) {
               throw {
                  name: 'Tag Mismatch Error',
                  message: 'Closing tag </' + tag_name + '> not found ' + this.line + ':' + this.row
               }
            }

            opening_tag_name = this.tag_stack.pop()[0];
            if (opening_tag_name !== tag_name) {
               throw {
                  name: 'Tag Mismatch Error',
                  message: 'Opening tag <' + opening_tag_name + '> does not match closing tag </' + tag_name + '> ' + this.line + ':' + this.row
               }
            }
         }
      } else {
         this.extract_remaining_tag();
      }

      return tag_output;
   };

   HTMLFilter.prototype.filter_attribute = function(tag_name) {
      var tag_spec, attribute_name, is_allowed, value, tag_spec;
      var is_in_spec, is_in_globals, is_wildcard, is_regex;

      tag_spec = this.get_tag_spec(tag_name);
      
      attribute_name = this.extract_attribute_name();
      
      this.extract_whitespace();

      is_in_spec = (!!tag_spec[attribute_name]);
      is_in_globals = (!!this.global_attrs[attribute_name]);
      is_wildcard = (!!tag_spec['*']);
      is_regex = (!!tag_spec['^$']);
      is_allowed = is_in_spec || is_in_globals || is_wildcard || is_regex;
      
      value = null;
      if (this.curr_char === '=') {
         this.next();
         value = this.filter_value(tag_name, attribute_name);
         if (!value) {
            is_allowed = false;
         }
      
      } else if (!ATTR_REGEX.test(this.curr_char) && this.curr_char !== '>') {
         this.next();
         is_allowed = false;
      } else if (tag_spec && tag_spec[attribute_name] === 'boolean') {
         value = True;
      }

      if (is_allowed) {
         if (value === true) {
            return attribute_name;
         } else if (value !== null) {
            return attribute_name + '=' + value;
         }
      }
      
      return null;
   };

   HTMLFilter.prototype.is_valid_unquoted_attr_char = function(char) {
      return !UNQUOTED_INVALID_REGEX.test(char) && !WHITESPACE_REGEX.test(char);
   };

   HTMLFilter.prototype.filter_value = function(tag_name, attribute_name) {
      var value, num_spaces, quote, rules, global_rules, new_value, tag_spec, matches;

      num_spaces = this.extract_whitespace().length;

      value = '';
      quote = '"';
      if (this.curr_char === "'" || this.curr_char === '"') {
         quote = this.curr_char;

         while (this.next() !== quote) {
            if (this.curr_char === '') {
               throw {
                  name: 'HTML Syntax Error',
                  message: 'Attribute quote not closed: <' + tag_name + ' ' + attribute_name + '>'
               };
            }

            value += this.curr_char;
         }

         this.next();
      } else if (num_spaces === 0 && this.is_valid_unquoted_attr_char(this.curr_char)) {
         value += this.curr_char;
         while (this.is_valid_unquoted_attr_char(this.next())) {
            value += this.curr_char;
         }
      }

      rules = null;
      global_rules = null;

      tag_spec = this.get_tag_spec(tag_name);
      if (tag_spec !== null) {
         if (tag_spec[attribute_name]) {
            rules = tag_spec[attribute_name];
         } else if (tag_spec['*']) {
            rules = tag_spec['*'];
         } else if (tag_spec['^$']) {
            matches = tag_spec['^$'].filter(function(pair) {
               return (pair[0] instanceof RegExp) && pair[0].test(attribute_name);
            });
            if (matches.length > 0) {
               rules = matches[0][1];
            }
         }
      }

      if (this.global_attrs && this.global_attrs[attribute_name]) {
         global_rules = this.global_attrs[attribute_name];
      }

      if (!rules && !global_rules) {
         return null;
      }

      new_value = null;

      if (rules) {
         new_value = this.purify_attribute(attribute_name, value, rules);
      }

      if (global_rules && (new_value == null)) {
         new_value = this.purify_attribute(attribute_name, value, global_rules);
      }

      if (new_value === null) {
         return null;
      } else if (new_value === true) {
         return true;
      } else {
         return quote + new_value + quote;
      }
   };
   
   HTMLFilter.prototype.purify_attribute = function(attribute_name, value, rules) {
      var candidate_values, allowed_values, allowed_values_set, i, rule_index, is_purified, parts, pure_value, new_class_value;

      parts = this.purify_value(value, rules, attribute_name);
      value = parts[0];
      is_purified = parts[1];

      if (!is_purified) {
         if (attribute_name === "class" && Object.prototype.toString.call(rules) == '[object Array]') {
            candidate_values = value.split(' ');
            allowed_values_set = {};
            allowed_values = [];

            for (i = 0; i != candidate_values.length; ++i) {
               for (rule_index = 0; rule_index != rules.length; ++rule_index) {
                  new_class_value = null;
                  if (rules[rule_index] instanceof RegExp) {
                     new_class_value = this.purify_regex(candidate_values[i], rules[rule_index]);
                  } else if (typeof rules === 'function') {
                     new_class_value = rules[rule_index](candidate_values[i]);
                  } else if (candidate_values[i] === rules[rule_index]) {
                     new_class_value = candidate_values[i];
                  }

                  if (new_class_value && !allowed_values_set[new_class_value]) {
                     allowed_values_set[new_class_value] = true;
                     allowed_values.push(new_class_value);
                  }
               }
            }
            
            if (allowed_values.length > 0) {
               value = allowed_values.join(' ');
            } else {
               value = null;
            }
         } else if (attribute_name === "style" && Object.prototype.toString.call(rules) == '[object Object]') {
            candidate_values = value.split(';');
            allowed_values = [];
            for (i = 0; i != candidate_values.length; ++i) {
               pure_value = this.purify_style(candidate_values[i], rules);
               if (pure_value !== '' && pure_value != null) {
                  allowed_values.push(pure_value);
               }
            }
            if (allowed_values.length > 0) {
               value = allowed_values.join(';') + ';';
            } else {
               value = null;
            }
         } else if (rules.length > 0) {
            if (rules.indexOf(value) < 0) {
               value = null;
            }
         }
      }

      return value;
   };

   HTMLFilter.prototype.purify_value = function(value, rules, attribute_name) {
      var purified = true;
      
      // disallow &# in values (can be used for encoding disallowed characters)
      if (UNICODE_REGEX.test(value)) {
         value = null;
      } else if (rules === "*") {
         value = value;
      } else if (rules instanceof RegExp) {
         value = this.purify_regex(value, rules);
      } else if (rules === "boolean") {
         if (value === '' || (attribute_name !== null && value === attribute_name)) {
            value = true;
         } else {
            value = null;
         }
      } else if (rules === "url") {
         value = value.trim();
         value = this.purify_url(value);
      } else if (rules === "url|empty") {
         value = value.trim();
         if (value !== '') {
            value = this.purify_url(value);
         }
      } else if (rules === "color") {
         value = this.purify_color(value);
      } else if (rules === "measurement") {
         value = this.purify_regex(value, MEASUREMENT_MATCH);
      } else if (rules === "int") {
         value = this.purify_int(value);
      } else if (rules === "alpha") {
         if (value === '') {
            value = null;
         } else {
            value = this.purify_regex(value, /^[a-zA-Z]+$/);
         }
      } else if (rules === "alphanumeric") {
         if (value === '') {
            value = null;
         } else {
            value = this.purify_regex(value, /^[a-zA-Z0-9]+$/);
         } 
      } else if (rules === "alpha|empty") {
         if (value !== '') {
            value = this.purify_regex(value, /^[a-zA-Z]+$/);
         }
      } else if (rules === "alphanumeric|empty") {
         if (value !== '') {
            value = this.purify_regex(value, /^[a-zA-Z0-9]+$/);
         }
      } else if (rules === "text") {
         value = this.purify_text(value, True);
      } else if (typeof rules === 'string' && rules.charAt(0) === '[' && rules.charAt(rules.length-1) === ']') {
         if (value === '') {
            value = null;
         } else {
            value = this.purify_set(value, rules.slice(1,-1));
         }
      } else if (typeof rules === 'function') {
         value = rules(value);
      } else {
         purified = false;
      }

      if (value === null && INVALID_ATTRIBUTE_REPLACEMENTS[rules]) {
         value = INVALID_ATTRIBUTE_REPLACEMENTS[rules];
      }

      return [value, purified];
   };

   HTMLFilter.prototype.escape_pattern = function(pattern, value, escaper) {
      var entities, match, new_text, chunks, chunk;

      entities = {};
      match = value.match(pattern);
      if (match) {
         match.forEach(function(escaped) {
            entities[escaped] = true;
         });
      }

      new_text = [];
      chunks = value.split(pattern);

      for (var i = 0; i < chunks.length; i++) {
         chunk = chunks[i]
         if (!entities[chunk]) {
            chunk = chunk.split('').map(escaper).join('')
         }
         new_text.push(chunk)
      }

      return new_text.join('');
   };

   HTMLFilter.prototype.purify_style = function(style, rules) {
      var parts, name, value, style_rules, is_purified;

      parts = style.split(':');

      if (parts.length !== 2) {
         return null;
      }

      name = parts[0].trim()
      value = parts[1].trim()

      if (CSS_ESCAPE.test(value)) {
         // disallow CSS unicode escaping
         return null;
      }

      if (rules[name]) {
         style_rules = rules[name];
         parts = this.purify_value(value, style_rules);
         value = parts[0];
         is_purified = parts[1];

         if (!is_purified) {
            if (style_rules.indexOf(value) < 0) {
               return null;
            }
         } else if (value === null || value === '') {
            return null;
         }
      } else {
         return null;
      }

      return name + ':' + value;
   };

   HTMLFilter.prototype.purify_color = function(value) {
     var i;
     var value = value.toLowerCase()

     for (i = 0; i !== HTML_COLORS.length; ++i) {
       if (value === HTML_COLORS[i]) {
         return value;
       }
     }

     if (HEX_MATCH.test(value)) {
       return value;
     }

     if (RGB_MATCH.test(value)) {
       return value;
     }

     if (RGBA_MATCH.test(value)) {
       return value;
     }

     if (HSL_MATCH.test(value)) {
       return value;
     }

     if (HSLA_MATCH.test(value)) {
       return value;
     }

     return null;
   };

   HTMLFilter.prototype.purify_url = function(url) {
      var parts, scheme, allowed_scheme, escaper;
      
      escaper = function(char) {
         return UNSAFE_URL_CHARS[char] || char;
      };

      url = this.escape_pattern(URL_ENCODING_MATCH, url, escaper);
      
      if (this.allowed_schemes.indexOf('//') < 0 && url.charAt(0) === '/' && url.charAt(1) === '/') {
        return null; // disallow protocol-relative URLs (possible XSS vector)
      }

      parts = url.split(':');
      scheme = '';
      if (parts.length > 1) {
         scheme = parts[0];
         if (scheme.indexOf('/') >= 0 || scheme.indexOf('#') >= 0) {
            scheme = '';
            url = null;
         } else {
            url = parts.slice(1).join(':');
         }
      }


      allowed_scheme = this.allowed_schemes.indexOf(scheme.toLowerCase()) >= 0;

      if (scheme === '') {
         return url;
      } else if (allowed_scheme) {
         return scheme + ':' + url;
      } else {
         return null;
      }
   };

   HTMLFilter.prototype.purify_int = function(value) {
      var intVal = parseInt(value);

      if (isNaN(intVal)) {
         return null;
      } else {
         return '' + intVal;
      }
   };

   HTMLFilter.prototype.purify_set = function(value, allowed_chars) {
      var regex, escaped_chars;

      escaped_chars = allowed_chars.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
      regex = new RegExp('^[' + escaped_chars + ']+$');
      
      return this.purify_regex(value, regex);
   };

   HTMLFilter.prototype.purify_regex = function(value, regex) {
      if (regex.test(value)) {
         return value;
      } else {
         return null;
      }
   };

   HTMLFilter.prototype.purify_text = function(value, include_quotes) {
      var _this = this;
      var escaper = function(char) {
         return _this.escape_data(char, include_quotes);
      };

      return this.escape_pattern(ENTITY_MATCH, value, escaper);
   };

   var filter_html = function(html, spec, allowed_schemes, text_filter, remove) {
      var html_filter = new HTMLFilter(spec, allowed_schemes, text_filter, remove);
      return html_filter.filter(html);
   };
   
   return {
      'filter_html': filter_html
   };
})();

if (typeof exports !== 'undefined') {
   exports = FilterHTML;
}
if (typeof module !== 'undefined') {
   module.exports = FilterHTML;
}
