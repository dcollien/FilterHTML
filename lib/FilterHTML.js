var FilterHTML = (function() {

   // browsers parse with an inert <template> element; elsewhere (Node) parse5 is used
   var parse5 = (typeof document === 'undefined' && typeof require === 'function') ? require('parse5') : null;

   var ATTR_NAME_REGEX = /^[a-z\-]+$/;
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
   var ATTRIBUTE_ESCAPE_CHARS = {
      '>': '&gt;',
      '<': '&lt;',
      '&': '&amp;',
      '"': '&quot;',
      "'": '&apos;'
   };
   var TEXT_FILTER_ESCAPE_CHARS = {
      '>': '&gt;',
      '<': '&lt;',
      '&': '&amp;'
   };

   var URL_ENCODING_MATCH = /(\%[0-9a-fA-F]{2})/g;

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

   // own properties only, so names like "constructor" never hit Object.prototype
   var has = function(obj, key) {
      return obj !== null && typeof obj === 'object' && Object.prototype.hasOwnProperty.call(obj, key);
   };

   var escape = function(value, table) {
      var i, ch, output = '';

      for (i = 0; i < value.length; ++i) {
         ch = value.charAt(i);
         output += has(table, ch) ? table[ch] : ch;
      }

      return output;
   };

   // Parsed nodes are converted to: strings (text), or {name, attrs: [[name, value]], children}
   var convert_nodes = function(nodes) {
      var i, node, result = [];

      for (i = 0; i < nodes.length; ++i) {
         node = nodes[i];
         if (node.nodeName === '#text') {
            result.push(parse5 ? node.value : node.data);
         } else if (node.tagName) {
            result.push(convert_element(node));
         }
      }

      return result;
   };

   var convert_element = function(node) {
      var i, attr, name, source_attrs, container, attrs = [];

      name = (parse5 ? node.tagName : node.localName).toLowerCase();
      source_attrs = parse5 ? node.attrs : node.attributes;

      for (i = 0; i < source_attrs.length; ++i) {
         attr = source_attrs[i];
         if (parse5 && attr.prefix) {
            attrs.push([(attr.prefix + ':' + attr.name).toLowerCase(), attr.value]);
         } else {
            attrs.push([attr.name.toLowerCase(), attr.value]);
         }
      }

      container = (name === 'template' && node.content) ? node.content : node;

      return {
         name: name,
         attrs: attrs,
         children: convert_nodes(container.childNodes)
      };
   };

   var parse = function(html) {
      var template;

      if (parse5) {
         return convert_nodes(parse5.parseFragment(html).childNodes);
      }

      if (typeof document === 'undefined') {
         throw new Error('FilterHTML needs a browser document or the parse5 package');
      }

      template = document.createElement('template');
      template.innerHTML = html;
      return convert_nodes(template.content.childNodes);
   };

   var HTMLFilter = function(spec, allowed_schemes, text_filter, remove) {
      this.spec = spec;
      this.global_attrs = has(spec, '*') ? spec['*'] : {};
      
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
         if (!has(this.spec, 'script')) {
           this.removals.push('script');
         }
         if (!has(this.spec, 'style')) {
           this.removals.push('style');
         }
      }
   };
   
   HTMLFilter.prototype.filter = function(html) {
      return this.filter_nodes(parse(html), [], this.text_filter);
   };

   HTMLFilter.prototype.filter_nodes = function(nodes, tag_stack, text_filter) {
      var i, node, filtered_text, output = '';

      for (i = 0; i < nodes.length; ++i) {
         node = nodes[i];
         if (typeof node !== 'string') {
            output += this.filter_element(node, tag_stack, text_filter);
         } else if (text_filter) {
            filtered_text = text_filter(escape(node, TEXT_FILTER_ESCAPE_CHARS), tag_stack);

            // the text filter returns HTML, which must also adhere to the spec
            output += this.filter_nodes(parse(filtered_text), tag_stack, null);
         } else {
            output += escape(node, HTML_ESCAPE_CHARS);
         }
      }

      return output;
   };

   HTMLFilter.prototype.filter_element = function(element, tag_stack, text_filter) {
      var tag_spec, tag_parts, tag_name, attributes, tag_output, contents;

      if (this.removals.indexOf(element.name) >= 0) {
         return '';
      }

      tag_spec = this.get_tag_spec(element.name, tag_stack);

      if (tag_spec === null) {
         // remove the tag, keep its contents
         return this.filter_nodes(element.children, tag_stack, text_filter);
      }

      if (tag_spec === false) {
         // remove the tag and its contents
         return '';
      }

      tag_parts = this.follow_aliases(element.name);
      tag_name = tag_parts[0];
      attributes = tag_parts[1].concat(this.filter_attributes(tag_name, element.attrs, tag_stack));

      tag_output = '<' + tag_name;
      if (attributes.length > 0) {
         tag_output += ' ' + attributes.join(' ');
      }
      tag_output += '>';

      if (VOID_ELEMENTS.indexOf(tag_name) >= 0) {
         return tag_output;
      }

      if (element.name === 'script' && tag_name === 'script') {
         // the spec explicitly allows scripts, so their contents pass through unchanged
         contents = element.children.filter(function(child) {
            return typeof child === 'string';
         }).join('');
      } else {
         contents = this.filter_nodes(element.children, tag_stack.concat([[tag_name, attributes]]), text_filter);
      }

      return tag_output + contents + '</' + tag_name + '>';
   };

   HTMLFilter.prototype.get_tag_spec = function(tag_name, tag_stack) {
      var tag_spec = has(this.spec, tag_name) ? this.spec[tag_name] : null;

      if (typeof(tag_spec) === 'function') {
         tag_spec = tag_spec(tag_name, tag_stack);
      }

      if (tag_spec === false) {
         return false;
      }

      return tag_spec || null;
   };

   HTMLFilter.prototype.follow_aliases = function(tag_name) {
      var tag_parts, alias_attributes;

      alias_attributes = [];

      while (has(this.spec, tag_name) && (typeof this.spec[tag_name] === 'string')) {
         tag_parts = this.spec[tag_name].split(' '); // follow aliases
         tag_name = tag_parts[0];
         if (tag_parts.length > 1) {
            alias_attributes = alias_attributes.concat(tag_parts.slice(1));
         }
      }

      return [tag_name, alias_attributes];
   };

   HTMLFilter.prototype.filter_attributes = function(tag_name, attrs, tag_stack) {
      var i, attribute_name, new_value, tag_spec, seen = {}, attributes = [];

      tag_spec = this.get_tag_spec(tag_name, tag_stack);
      if (!tag_spec || typeof tag_spec !== 'object') {
         tag_spec = {};
      }

      for (i = 0; i < attrs.length; ++i) {
         attribute_name = attrs[i][0];

         // browsers keep the first of any repeated attribute
         if (has(seen, attribute_name) || !ATTR_NAME_REGEX.test(attribute_name)) {
            continue;
         }
         seen[attribute_name] = true;

         new_value = this.filter_value(tag_spec, attribute_name, attrs[i][1]);
         if (new_value === true) {
            attributes.push(attribute_name);
         } else if (new_value !== null) {
            attributes.push(attribute_name + '="' + escape(new_value, ATTRIBUTE_ESCAPE_CHARS) + '"');
         }
      }

      return attributes;
   };

   HTMLFilter.prototype.filter_value = function(tag_spec, attribute_name, value) {
      var rules, global_rules, new_value, matches;

      rules = null;
      global_rules = null;

      if (has(tag_spec, attribute_name)) {
         rules = tag_spec[attribute_name];
      } else if (has(tag_spec, '*')) {
         rules = tag_spec['*'];
      } else if (has(tag_spec, '^$')) {
         matches = tag_spec['^$'].filter(function(pair) {
            return (pair[0] instanceof RegExp) && pair[0].test(attribute_name);
         });
         if (matches.length > 0) {
            rules = matches[0][1];
         }
      }

      if (has(this.global_attrs, attribute_name)) {
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

      if (new_value === null || new_value === undefined) {
         return null;
      } else if (new_value === true) {
         return true;
      } else {
         return '' + new_value;
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

                  if (new_class_value && !has(allowed_values_set, new_class_value)) {
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
      
      if (rules === "*") {
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
         // any text is allowed; it is HTML-encoded on output
         value = value;
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

      if (value === null && typeof rules === 'string' && has(INVALID_ATTRIBUTE_REPLACEMENTS, rules)) {
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
         if (!has(entities, chunk)) {
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

      if (has(rules, name)) {
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
