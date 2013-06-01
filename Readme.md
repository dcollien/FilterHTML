FilterHTML
---------


A dictionary-defined whitelisting HTML filter. Useful for filtering HTML to leave behind a supported or safe sub-set.

Python and JavaScript versions

Python installation:
    
    pip install FilterHTML

What this does:
 - Lets you easily define a subset of HTML and it filters out everything else
 - Ensures there's no unicode encoding in attributes (e.g. &#58; or \3A for CSS)
 - Lets you use regular expressions, lists, functions or built-ins as rules/filters
 - Lets you filter or match attributes on tags
 - Lets you filter or match individual CSS styles in style attributes
 - Lets you define allowed classes as a list
 - Has a "url" built-in for checking allowed schemes (e.g. http, https, mailto, ftp)
 - Lets you use your own functions to check attributes (if you need tighter control)
 - Helps to reduce XSS/code injection vulnerabilities
 - Runs in Python or Javascript (the JS port is available for client-side checking if you want)

What this doesn't do:
 - Clean up tag soup (use something else for that, like BeautifulSoup): this assumes the HTML is valid and complete
 - Claim to be XSS-safe out of the box: it relies on you being somewhat careful with your whitelist specification


Define an allowed HTML subset as a JSON object (for the JS version) or a Python dictionary, e.g.

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
