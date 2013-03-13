FilterHTML
---------


A dictionary-defined whitelisting HTML filter. Useful for filtering HTML to leave behind a supported or safe sub-set.

Python and JavaScript versions

Define an allowed HTML subset as a JSON object or Python dictionary, e.g.

    spec = {

      "div": {
        // list allowed attribute values, as a list
        "class": [
           "container",
           "content"
        ]
      },

      "p": {
        "class": [
           "centered"
        ],
        // style parsing
        "style": {
          "color": re.compile(r'^#[0-9A-Fa-f]{6}$')
        }
      },

      "a": {
        // parse urls to ensure there's no javascript, by using the "url" string.
        // allowed schemes are 'http', 'https', 'mailto', and 'ftp' (as well as local URIs)
        "href": "url",
        "target": [
           "_blank"
        ]
      },

      "img": {
        "src": "url",
        // make sure these fields are integers, by using the "int" string
        "border": "int",
        "width": "int",
        "height": "int"
      },

      "input": {
        // only allow alphabetical characters
        "type": "alpha",
        // allow any of these characters (within the [])
        "name": "[abcdefghijklmnopqrstuvwxyz-]",
        // allow alphabetical and digit characters
        "value": "alphanumeric"
      },

      // filter out all attributes for these tags
      "hr": {},
      "br": {},
      "strong": {},

      "i": {
        // use a regex match
        // in python you can use re.compile
        "class": /^icon-[a-z0-9_]+$/
      },

      // global attributes (allowed on all elements):
      // (N.B. only applies to tags already supplied as keys)
      // element's specific attributes take precedence, but if they are all filtered out these global rules are applied to the original attribute value
      
      "*": {
        "class": ["text-left", "text-right", "text-centered"]
      },

      // aliases (convert one tag to another):

      // convert <b> tags to <strong> tags
      "b": "strong",

      // convert <center> tags to <p class="text-centered"> tags
      "center": "p class=\"text-centered\""
    }
