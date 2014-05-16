FilterHTML
---------
v0.3 - White-list tags, attributes, classes, styles. With tag-specific text filtering and tag contents removal.

A dictionary-defined white-listing HTML filter. Useful for filtering HTML to leave behind a supported or safe sub-set.

Python and JavaScript versions

Python installation:
    
    pip install FilterHTML

Node.js installation:

    npm install filterhtml

Browser: copy `./lib/FilterHTML.js` into your project

Example:

    import FilterHTML

    # only allow:
    #   <a> tags with valid href URLs
    #   <img> tags with valid src URLs and measurements
    #   <span> tags with valid color styles
    whitelist = {
      'a': {
        'href': 'url',
        'target': [
          '_blank',
          '_self'
        ],
        'class': [
          'button'
        ]
      },

      'img': {
        'src': 'url',
        'width': 'measurement',
        'height': 'measurement'
      },

      'span': {
        'style': {
          'color': 'color',
          'background-color': 'color'
        }
      }
    }

    # perform replacements on text (between tags)
    def replace_text(text, tags):
      return text.replace('sad', '<strong>happy</strong>')

    # filter the unfiltered_html, using the above whitelist, using specified allowed url schemes, and a text replacement function
    filtered_html = FilterHTML.filter_html(unfiltered_html, whitelist, ('http', 'https', 'mailto', 'ftp'), replace_text)

    # simpler usage: filter using the default (same as above) url schemes, and no replacement function:
    filtered_html = FilterHTML.filter_html(unfiltered_html, whitelist)



What this does:
 - Lets you easily define a subset of HTML and it filters out everything else
 - Ensures there's no unicode encoding in attributes (e.g. &amp;#58; or \3A for CSS)
 - Lets you use regular expressions, lists, function delegates or built-ins as rules/filters
 - Lets you filter or match attributes on tags
 - Lets you filter or match individual CSS styles in style attributes
 - Lets you define allowed classes as a list
 - Lets you specify a filtering function delegate for modifying text between tags (e.g. url auto-linking, emoticon parsing, #tagging, @mentioning, etc.), the output is also HTML filtered
 - Lets you convert one tag into another (with specified attributes)
 - Lets you completely remove contents of specified tags from HTML
 - Helps to reduce XSS/code injection vulnerabilities
 - Runs server-side in Python (e.g. Flask, Bottle, Django) or Javascript (e.g. Node) 
 - The Javascript port can also be used for client-side filtering

What this doesn't do:
 - Clean up tag soup (use something else for that, like BeautifulSoup): this assumes the HTML is valid and complete. It will throw exceptions if it detects unclosed opening tags, or extra closing tags.
 - Claim to be XSS-safe out of the box: be careful with your white-list specification and test it thoroughly (here's a handy resource: https://www.owasp.org/index.php/XSS_Filter_Evasion_Cheat_Sheet)

### Class and Style filtering
 - parses the 'class' attribute into a list of values to match against allowed classes (list of values or regular expressions)
 - parses the 'style' attribute to match each style against a list of allowed styles, each with individual rules

 e.g.

    {
      'div': {
        # style filtering:
        'style': {
          'width': 'measurement',
          'height': 'measurement',
          'background-color': 'color',
          'text-align': ['left', 'right', 'center', 'justify', 'inherit'],
          'border': border_filter_function, # implement your own function,
          'border-radius': re.compile(r'^\d+px$')
        }
      },

      'span': {
        # class filtering (a list of allowed matches, strings, regex or functions):
        'class': [
          'icon',
          re.compile(r'^icon\-[a-zA-Z0-9\-]+$')
        ]
      }
    }

### Text filtering/modification
 - Text (between tags) can be filtered or modified with a delegate function. This function is passed each string of text between tags, as well as a list of the tags this string is inside (and their attributes). The string is replaced with the output of this function, and it is also filtered according to the supplied white-list specification. 

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

    # script and style tag contents can be removed:
    result = FilterHTML.filter_html(html, spec, text_filter=urlize, remove=['script', 'style'])


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

For regular expression filters, you can use /pattern/modifiers syntax in JavaScript (or new RegExp), or in Python: re.compile()

Python example whitelist:

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
        # by default allowed schemes are 'http', 'https', 'mailto', and 'ftp' (as well as local URIs)
        # this can be changed by passing in allowed_schemes=('http', 'myscheme')
        "href": "url",
        "target": [
           "_blank"
        ]
      },

      "img": {
        "src": "url",
        # make sure these fields are integers, by using the "int" string
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

