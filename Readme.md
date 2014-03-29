FilterHTML
---------
v0.2 - White-list tags, attributes, classes, styles, and now with text filtering!

A dictionary-defined white-listing HTML filter. Useful for filtering HTML to leave behind a supported or safe sub-set.

Python and JavaScript versions

Python installation:
    
    pip install FilterHTML

What this does:
 - Lets you easily define a subset of HTML and it filters out everything else
 - Ensures there's no unicode encoding in attributes (e.g. &amp;#58; or \3A for CSS)
 - Lets you use regular expressions, lists, function delegates or built-ins as rules/filters
 - Lets you filter or match attributes on tags
 - Lets you filter or match individual CSS styles in style attributes
 - Lets you define allowed classes as a list
 - Lets you specify a filtering function delegate for modifying text between tags (e.g. url auto-linking, emoticon parsing, #tagging, @mentioning, etc.), the output is also HTML filtered
 - Helps to reduce XSS/code injection vulnerabilities
 - Runs server-side in Python (e.g. Flask, Bottle, Django) or Javascript (e.g. Node) 
 - The Javascript port can also be used for client-side filtering

What this doesn't do:
 - Clean up tag soup (use something else for that, like BeautifulSoup): this assumes the HTML is valid and complete. It will throw exceptions if it detects unclosed opening tags, or extra closing tags.
 - Claim to be XSS-safe out of the box: be careful with your white-list specification and test it thoroughly (here's a handy resource: https://www.owasp.org/index.php/XSS_Filter_Evasion_Cheat_Sheet)

### Class and Style filtering
 - parses the 'class' attribute into a list of values to match against allowed classes (list of values or regular expressions)
 - parses the 'style' attribute to match each style against a list of allowed styles, each with individual rules

### Text filtering/modification
 - Text (between tags) can be filtered or modified with a delegate function. This function is passed each string of text between tags, as well as a list of the tags this string is inside (and their attributes). The string is replaced with the output of this function, and it is also filtered according to the supplied white-list specification. 

### Built-In Filters:
 - "url", for parsing URLs and matching against allowed schemes (http://, ftp://, mailto:, etc.)
 - "color", for matching an HTML color value (either a string, like "red", "blue", etc. or "#fff", "#f0f0f0", or valid "rgb", "rgba", "hsl", or "hsla" values)
 - "measurement", for matching style measurements, e.g. "42px", "10%", "6em", etc.
 - "int", for matching an integer
 - "alpha", for matching alphabetical characters
 - "alphanumeric", for matching alphabetical and digit characters
 - "[allowedchars]", for allowing characters specified between starting and ending "[ ]"
 Matching can also be done against regular expressions or a list of allowed values. Values can also be passed through custom filtering functions.

### White-list
Define an allowed HTML subset as a JSON object (for the JS version) or a Python dictionary.

In JavaScript you can use /pattern/modifiers syntax (or new RegExp), or in Python: re.compile() in order to define regular expression filters.

e.g.

    spec = {

      "div": {
        # list allowed attribute values, as a list
        "class": [
           "container",
           "content"
        ]
      },

      "p": {
        "class": [
           "centered"
        ],
        # style parsing
        "style": {
          "color": re.compile(r'^#[0-9A-Fa-f]{6}$')
        }
      },

      "a": {
        # parse urls to ensure there's no javascript, by using the "url" string.
        # disallow &# unicode encoding
        # allowed schemes are 'http', 'https', 'mailto', and 'ftp' (as well as local URIs)
        "href": "url",
        "target": [
           "_blank"
        ]
      },

      "img": {
        "src": "url",
        # make sure these fields are integers, by using the "int" string
        "border": "int",
        "width": "int",
        "height": "int"
      },

      "input": {
        # only allow alphabetical characters
        "type": "alpha",
        # allow any of these characters (within the [])
        "name": "[abcdefghijklmnopqrstuvwxyz-]",
        # allow alphabetical and digit characters
        "value": "alphanumeric"
      },

      # filter out all attributes for these tags
      "hr": {},
      "br": {},
      "strong": {},

      "i": {
        # use a regex match
        # in javascript you can use /this style/ regex.
        "class": re.compile(r'^icon-[a-z0-9_]+$/')
      },

      # global attributes (allowed on all elements):
      # (N.B. only applies to tags already supplied as keys)
      # element's specific attributes take precedence, but if they are all filtered out 
      # these global rules are applied to the original attribute value
      
      "*": {
        "class": ["text-left", "text-right", "text-centered"]
      },

      # aliases (convert one tag to another):

      # convert <b> tags to <strong> tags
      "b": "strong",

      # convert <center> tags to <p class="text-centered"> tags
      "center": "p class=\"text-centered\""
    }

### Text Filtering

The following python example does simple auto-linking of URLs, but only those not already inside 'a' tags.
N.B. the output HTML of the urlize function is also HTML filtered using the same spec.

    URLIZE_RE = '(%s)' % '|'.join([
        r'<(?:f|ht)tps?://[^>]*>',
        r'\b(?:f|ht)tps?://[^)<>\s]+[^.,)<>\s]',
    ])

    # second argument is a list of tags which this text is inside,
    # each element a tuple: (tag_name, attributes)
    def urlize(text, stack):
      is_inside_a_tag = False
      for tag in stack:
        tag_name, attributes = tag
        if tag_name == 'a':
          is_inside_a_tag = True
          break

      if is_inside_a_tag:
        return text
      else:
        return re.sub(URLIZE_RE, r'<a href="\1">\1</a>', text)


    result = FilterHTML.filter_html(html, spec, text_filter=urlize)
