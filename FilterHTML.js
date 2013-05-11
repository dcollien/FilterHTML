var FilterHTML = (function() {

   var TAG_REGEX = /^[a-z1-6]$/;
   var ATTR_REGEX = /^[a-z\-]$/;
   var WHITESPACE_REGEX = /^\s$/;
   var UNICODE_REGEX = /^.*&#.*$/;

   var HTMLFilter = function(spec, allowed_schemes) {
      this.html = '';
      this.filtered_html = '';
      this.spec = spec;
      this.global_attrs = spec['*'];
      
      if (allowed_schemes) {
         this.allowed_schemes = allowed_schemes;
      } else {
         this.allowed_schemes = ['http', 'https', 'mailto', 'ftp'];
      }
   };
   
   HTMLFilter.prototype.filter = function(html) {
      this.html = html;
      this.filtered_html = '';
      this.curr_index = 0;
      while (this.next()) {
         if (this.curr_char === '<') {
            this.filter_tag();
         } else {
            if (this.curr_char === '>') {
               this.filtered_html += '&gt;';
            } else {
               this.filtered_html += this.curr_char;
            }
         }
      }

      return this.filtered_html;
   };

   HTMLFilter.prototype.next = function() {
      this.curr_char = this.html.charAt(this.curr_index);
      this.curr_index++;
      return this.curr_char;
   };

   HTMLFilter.prototype.filter_tag = function() {
      if (this.next() === '/') {
         this.next();
         this.filter_closing_tag();
      } else {
         this.filter_opening_tag();
      }
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
      var tag_name, tag_parts, attributes, attribute;
      this.extract_whitespace();

      tag_name = this.extract_tag_name();

      tag_parts = this.follow_aliases(tag_name);
      tag_name = tag_parts[0];
      attributes = tag_parts[1];

      if (this.spec[tag_name]) {
         while (this.curr_char !== '>' && this.curr_char !== '') {
            this.extract_whitespace();
            attribute = this.filter_attribute(tag_name);
            if (attribute) {
               attributes.push(attribute);
            }
         }

         this.filtered_html += '<' + tag_name;

         if (attributes.length > 0) {
            this.filtered_html += ' ' + attributes.join(' ');
         }

         this.filtered_html += '>';
      } else {
         this.extract_remaining_tag();
      }
   };

   HTMLFilter.prototype.filter_closing_tag = function() {
      var tag_name, tag_parts;

      this.extract_whitespace();

      tag_name = this.extract_tag_name();
      tag_parts = this.follow_aliases(tag_name);
      tag_name = tag_parts[0];

      if (this.spec[tag_name]) {
         this.extract_whitespace();
         if (this.curr_char === '>') {
            this.filtered_html += '</' + tag_name + '>';
            return;
         }
      } else {
         this.extract_remaining_tag();
      }
   };

   HTMLFilter.prototype.filter_attribute = function(tag_name) {
      var tag_spec, attribute_name, whitespace, is_allowed, value;

      tag_spec = this.spec[tag_name];
      
      attribute_name = this.extract_attribute_name();
      
      whitespace = this.extract_whitespace();

      is_allowed = (!!tag_spec[attribute_name]) || (!!this.global_attrs[attribute_name]);
      
      value = null;
      if (this.curr_char === '=') {
         this.next();

         this.extract_whitespace();
         value = this.filter_value(tag_name, attribute_name);
         if (!value) {
            is_allowed = false;
         }
      
      } else if (!ATTR_REGEX.test(this.curr_char) && this.curr_char !== '>') {
         this.next();
         is_allowed = false;
      }

      if (is_allowed) {
         return attribute_name + '=' + value;
      } else {
         return null;
      }
   };


   HTMLFilter.prototype.filter_value = function(tag_name, attribute_name) {
      var value, quote, rules, global_rules, new_value;

      value = '';
      quote = '"';
      if (this.curr_char === "'" || this.curr_char === '"') {
         quote = this.curr_char;

         while (this.next() !== quote) {
            if (this.curr_char === '') {
               break;
            }

            value += this.curr_char;
         }

         this.next();
      }

      rules = this.spec[tag_name][attribute_name];
      global_rules = null;

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

      if (global_rules && (new_value == null || new_value == '')) {
         new_value = this.purify_attribute(attribute_name, value, global_rules);
      }

      if (!new_value || new_value === '') {
         return null;
      } else {
         return quote + new_value + quote;
      }
   };
   
   HTMLFilter.prototype.purify_attribute = function(attribute_name, value, rules) {
      var candidate_values, allowed_values, i, isPurified, parts, pure_value;

      parts = this.purify_value(value, rules);
      value = parts[0];
      isPurified = parts[1];

      if (!isPurified) {
         if (attribute_name === "class") {
            candidate_values = value.split(' ');
            allowed_values = [];
            for (i = 0; i != candidate_values.length; ++i) {
               if (rules.indexOf(candidate_values[i]) >= 0) {
                  allowed_values.push(candidate_values[i]);
               }
            }
            value = allowed_values.join(' ');
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
               value = '';
            }
         } else if (rules.length > 0) {
            if (rules.indexOf(value) < 0) {
               value = '';
            }
         }
      }

      return value;
   };

   HTMLFilter.prototype.purify_value = function(value, rules) {
      var purified = true;
      if (rules instanceof RegExp) {
         value = this.purify_regex(value, rules);
      } else if (rules === "url") {
         value = this.purify_url(value);
      } else if (rules === "int") {
         value = this.purify_int(value);
      } else if (rules === "alpha") {
         value = this.purify_regex(value, /^[a-zA-Z]+$/);
      } else if (rules === "alphanumeric") {
         value = this.purify_regex(value, /^[a-zA-Z0-9]+$/);
      } else if (typeof rules === 'string' && rules.charAt(0) === '[' && rules.charAt(rules.length-1) === ']') {
         value = this.purify_set(value, rules.slice(1,-1));
      } else if (typeof rules === 'function') {
         value = rules(value);
      } else {
         purified = false;
      }

      return [value, purified];
   };

   HTMLFilter.prototype.purify_style = function(style, rules) {
      var parts, name, value, style_rules, isPurified;

      parts = style.split(':');

      if (parts.length !== 2) {
         return null;
      }

      name = parts[0].trim()
      value = parts[1].trim()

      if (rules[name]) {
         style_rules = rules[name];
         parts = this.purify_value(value, style_rules);
         value = parts[0];
         isPurified = parts[1];

         if (!isPurified) {
            if (style_rules.indexOf(value) < 0) {
               return null;
            }
         }
      } else {
         return null;
      }

      return name + ': ' + value;
   };

   HTMLFilter.prototype.purify_url = function(url) {
      var parts, scheme, allowed_scheme;

      // disallow &# in urls (can be used for encoding disallowed characters)
      if (UNICODE_REGEX.text(url)) {
         return '#';
      }

      parts = url.split(':');
      scheme = '';
      if (parts.length > 1) {
         scheme = parts[0];
         if (scheme.indexOf('/') >= 0 || scheme.indexOf('#') >= 0) {
            scheme = '';
            url = '#';
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
         return '#';
      }
   };

   HTMLFilter.prototype.purify_int = function(value) {
      var intVal = parseInt(value);

      if (isNaN(intVal)) {
         return '';
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
         return '';
      }
   };


   var filter_html = function(html, spec) {
      var html_filter = new HTMLFilter(spec);
      return html_filter.filter(html);
   };

   return {
      'filter_html': filter_html
   };
})();

if (module) {
   module.exports = FilterHTML;
}

