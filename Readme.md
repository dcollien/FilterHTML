FilterHTML
---------
v0.5 - White-list tags, attributes, classes, styles. With tag-specific text filtering and tag contents removal.

A dictionary-defined white-listing HTML filter. Useful for filtering HTML to leave behind a supported or safe sub-set.

- Simple and Powerful
- No dependencies
- Python and JavaScript versions, each a **single file**:
 - [FilterHTML.py](./FilterHTML.py)
 - [FilterHTML.js](./lib/FilterHTML.js)

Python installation:
    
    pip install FilterHTML

Node.js installation:

    npm install filterhtml

Browser: use `./lib/FilterHTML.js` in a &lt;script&gt; tag

Example:

```python
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
```


What this does:
 - Lets you **easily define a subset of HTML** and it filters out everything else
 - Ensures there's **no unicode** encoding in attributes (e.g. &amp;#58; or \3A for CSS)
 - Lets you use **regular expressions, lists, function delegates or built-ins** as rules/filters
 - Lets you filter or match **attributes** on tags
 - Lets you filter or match individual **CSS styles** in style attributes
 - Lets you define **allowed classes** as a list
 - Lets you specify a function delegate to define the specification for a tag, **depending on which tags it is inside**
 - Lets you specify a function delegate for modifying or **filtering text nodes**, i.e. text between tags (e.g. url auto-linking, emoticon parsing, #tagging, @mentioning, etc.), the output is also HTML filtered
 - Lets you **convert one tag into another** (with specified attributes)
 - Lets you **completely remove contents of specified tags** from HTML
 - Runs server-side in **Python** (e.g. Flask, Bottle, Django) or **JavaScript** (e.g. Node.JS, IO.js, **Browser**) 
 - Really helps to reduce XSS/code injection vulnerabilities

What this doesn't do:
 - Clean up tag soup (use something else for that, like BeautifulSoup): this assumes the HTML is valid and complete. It will throw exceptions if it detects unclosed opening tags, or extra closing tags.
 - Claim to be XSS-safe out of the box: be careful with your white-list specification and test it thoroughly (here's a handy resource: https://www.owasp.org/index.php/XSS_Filter_Evasion_Cheat_Sheet).

### Class and Style filtering
 - parses the 'class' attribute into a list of values to match against allowed classes (list of values or regular expressions)
 - parses the 'style' attribute to match each style against a list of allowed styles, each with individual rules


 e.g.
```python
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
```

### Text filtering/modification
 - Text (between tags) can be filtered or modified with a delegate function. This function is passed each string of text between tags, as well as a list of the tags this string is inside (and their attributes). The string is replaced with the output of this function, and it is also filtered according to the supplied white-list specification. 

The following python example does simple auto-linking of URLs, but only those not already inside 'a' tags.
N.B. the output HTML of the urlize function is also HTML filtered using the same spec.
```python
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
```

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
Define an allowed HTML subset as a JavaScript Object/Python Dictionary.

For regular expression filters, you can use /pattern/modifiers syntax in JavaScript (or new RegExp), or in Python: re.compile()

White-list format for allowing a tag can use many combinations of different filtering options, e.g.
```python
{
  "tag_name_a": {
    # attribute filtering by list of allowed values, built-in, regex, function delegate,
    # or a list of these types
    "attribute_a": ["allowed-value", "another-allowed-value"],
    "attribute_b": "url",
    "attribute_c": re.compile(r'^regex$'),
    "attribute_d": attribute_filtering_function,
    "attribute_e": [
      "allowed-value",
      re.compile(r'^regex$'),
      attribute_filtering_function
    ],

    # class filtering by a list of allowed values, or class-name matching regex
    "class": [
      "allowed-class-name",
      "another-allowed-class-name",
      re.compile(r'^class-name-regex$')
    ],

    # style filtering by object of allowed styles
    # filtered by: build-in, list of allowed values, regex, function delegate
    "style": {
      "style-name-a": "color",
      "style-name-b": [
        "value-1", "value-2"
      ],
      "style-name-c": re.compile(r'^regex$'),
      "style-name-d": style_filtering_functon
    }
  },

  # Allow this tag, but no attributes
  "tag_name_b": {},

  # Use a function delegate to specify this tag's white-list
  "tag_name_c": tag_filtering_function,

  # Remove this tag, and all its contents
  "tag_name_d": false,

  # Unlisted tags will be removed, but their contents left in-tact
}
```

White-list tag filtering functions are defined as:
```python
def tag_filtering_function(tag_name, tag_stack):
  # tag_name: the name of the tag being filtered
  # tag_stack: a list of (tag_name, attributes) for each tag
  #            above the current tag (in its parsing context)
  #            where the last in the list is the direct parent tag

  # Delete this tag and all its contents
  return False

  # Delete this tag, but not its contents
  return None

  # Return a custom specification for how to filter this tag
  return {
    'attribute_name': ['attribute_value']
  }
```

Attribute/Style filtering functions are defined as:

```python
def attr_filter(attribute_value):
  return "new-attribute-value"
  # or return None, or return '' to remove this attribute

def style_filter(style_value):
  return "new-style-value"
  # or return None, or return '' to remove this style
```
Python example whitelist:
```python
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
```
