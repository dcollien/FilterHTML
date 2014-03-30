var HTML_SPEC = {
  'span': {
    'class': [
      'pull-left',
      'pull-right',
      'glyphicon',
      /^glyphicon\-[a-zA-Z0-9\-]+$/,
      'label',
      'label-default',
      'label-primary',
      'label-success',
      'label-info',
      'label-warning',
      'label-danger',
      'badge',
      'badge-default',
      'badge-primary',
      'badge-success',
      'badge-info',
      'badge-warning',
      'badge-danger'
    ],

    'style': {
      'color': 'color',
      'background-color': 'color',
      'text-decoration': [
        'underline'
      ]
    }
  },

  'section': {},
  'code': {},
  'kbd': {},

  'div': {
    'style': {
      'color': 'color',
      'background-color': 'color'
    },
    'class': [
      'jumbotron',
      'pull-left',
      'pull-right',
      'center-block',
      'clearfix',
      'alert',
      'alert-success',
      'alert-info',
      'alert-warning',
      'alert-danger',
      'progress',
      'progress-striped',
      'progress-bar',
      'progress-bar-success',
      'progress-bar-info',
      'progress-bar-warning',
      'progress-bar-danger',
      'active',
      'media',
      'panel',
      'panel-primary',
      'panel-success',
      'panel-info',
      'panel-warning',
      'panel-danger',
      'panel-default',
      'panel-body',
      'panel-heading',
      'panel-footer',
      'well',
      'well-lg',
      'well-sm'
    ],

    'style': {
      'width': 'measurement'
    }
  },

  'a': {
    'href': 'url',
    'target': [
      '_blank'
    ],
    'class': [
      'pull-right',
      'pull-left',
      'btn',
      'btn-default',
      'btn-primary',
      'btn-success',
      'btn-info',
      'btn-warning',
      'btn-danger',
      'btn-link',
      'btn-lg',
      'btn-sm',
      'btn-xs',
      'btn-block',
      'active',
      'disabled',
      'alert-link'
    ]
  },

  'img': {
    'src': 'url',
    'alt': /^[\w\s]+$/,
    'class': [
      'img-responsive',
      'img-rounded',
      'img-circle',
      'img-thumbnail',
      'media-object',
      'pull-left',
      'pull-right'
    ],       
    'width': 'measurement',
    'height': 'measurement'
  },

  'p': {
    'class': [
      'lead',
      'text-left',
      'text-center',
      'text-right',
      'text-justify',
      'text-muted',
      'text-primary',
      'text-success',
      'text-info',
      'text-warning',
      'text-danger',
      'bg-primary',
      'bg-success',
      'bg-info',
      'bg-warning',
      'bg-danger',
      'list-group-item-text'
    ]
  },

  'table': {
    'summary': /^[\w\s]+$/,
    'class': [
      'table',
      'table-striped',
      'table-bordered',
      'table-hover',
      'table-condensed',
      'table-responsive'
    ]
  },
  'thead': {},
  'tbody': {},
  'tfoot': {},

  'tr': {
    'class': [
      'active',
      'success',
      'info',
      'warning',
      'danger'
    ]
  },

  'th': {
    'class': [
      'active',
      'success',
      'info',
      'warning',
      'danger'
    ],
    'style': {
      'text-align': ['left', 'right', 'center', 'justify', 'inherit']
    },
    'scope': ['row', 'col', 'rowgroup', 'colgroup'],
    'rowspan': /^\d+$/,
    'colspan': /^\d+$/
  },

  'td': {
    'class': [
      'active',
      'success',
      'info',
      'warning',
      'danger'
    ],
    'style': {
      'text-align': ['left', 'right', 'center', 'justify', 'inherit']
    },
    'scope': ['row', 'col', 'rowgroup', 'colgroup'],
    'rowspan': /^\d+$/,
    'colspan': /^\d+$/
  },

  'h1': {
    'class': [
      'media-heading',
      'list-group-item-heading',
      'panel-title'
    ]
  },
  'h2': {
    'class': [
      'media-heading',
      'list-group-item-heading',
      'panel-title'
    ]
  },
  'h3': {
    'class': [
      'media-heading',
      'list-group-item-heading',
      'panel-title'
    ]
  },
  'h4': {
    'class': [
      'media-heading',
      'list-group-item-heading',
      'panel-title'
    ]
  },
  'h5': {
    'class': [
      'media-heading',
      'list-group-item-heading',
      'panel-title'
    ]
  },
  'h6': {
    'class': [
      'media-heading',
      'list-group-item-heading',
      'panel-title'
    ]
  },

  'small': {},
  'strong': {},
  'em': {},
  'abbr': {
    'title': /^[\w\s]+$/,
    'class': [
      'initialism'
    ]
  },
  'address': {},
  'blockquote': {
    'class': [
      'blockquote-reverse'
    ]
  },
  'footer': {},
  'cite': {
    'title': /^[\w\s]+$/
  },

  'ul': {
    'class': [
      'list-unstyled',
      'list-inline',
      'media-list',
      'list-group'
    ]
  },

  'ol': {
    'start': 'int',
    'type': [
      '1',
      'A',
      'a',
      'I',
      'i'
    ]
  },

  'li': {
    'class': [
      'media',
      'list-group-item',
      'list-group-item-success',
      'list-group-item-info',
      'list-group-item-warning',
      'list-group-item-danger',
      'active'
    ]
  },

  'dl': {
    'class': [
      'dl-horizontal'
    ]
  },

  'dt': {},

  'hr': {},
  'sup': {},
  'sub': {},

  // aliases
  'center': 'p class="text-center"',
  'script': 'code',
  'b': 'strong',
  'i': 'em',
  'u': 'span style="text-decoration: underline"'
};

