HTML_WHITELIST = {
	'div': {
		'class': [
			'well',
			'well-small',
			'well-large',

			'pull-right',
			'pull-left',
			'clearfix',

			'media',
			'media-body',

			'page-header',
			'hero-unit',

			'alert',
			'alert-block',
			'alert-error',
			'alert-success',
			'alert-info',

			'thumbnail'
		]
	},

	'span': {
		'class': [
			'badge',
			'badge-success',
			'badge-warning',
			'badge-important',
			'badge-info',
			'badge-inverse',
			
			'label',
			'label-success',
			'label-warning',
			'label-important',
			'label-info',
			'label-inverse'
		]
	},
	
	'h1': {
		'name': 'alphanumeric',
		'class': [
			'media-heading'
		]
	},
	'h2': {
		'name': 'alphanumeric',
		'class': [
			'media-heading'
		]
	},
	'h3': {
		'name': 'alphanumeric',
		'class': [
			'media-heading'
		]
	},
	'h4': {
		'name': 'alphanumeric',
		'class': [
			'media-heading'
		]
	},
	'h5': {
		'name': 'alphanumeric',
		'class': [
			'media-heading'
		]
	},
	'h6': {
		'name': 'alphanumeric',
		'class': [
			'media-heading'
		]
	},

	'a': {
		'href': 'url',
		'target': [
			'_blank'
		],
		'class': [
			'thumbnail',

			'pull-right',
			'pull-left',
			'clearfix',

			'btn',
			'btn-primary',
			'btn-info',
			'btn-success',
			'btn-warning',
			'btn-danger',
			'btn-inverse',
			'btn-large',
			'btn-small',
			'btn-mini',
			'btn-block',
			'disabled'
		]
	},

	'img': {
		'src': 'url',
		'alt': re.compile(r'^[\w\s]+$'),
		'width': re.compile(r'^\d+(px)?$'),
		'height': re.compile(r'^\d+(px)?$'),
		'class': [
			'media-object',
			'img-rounded',
			'img-circle',
			'img-polaroid'
		]
	},

	'hr': {
		'class': [
			'clearfix'
		]
	},
	'br': {
		'class': [
			'clearfix'
		]
	},
	'b': {},
	'strong': {},
	'small': {},
	'em': {},
	'i': {
		'class': re.compile(r'^icon-[a-z0-9_]+$')
	},

	'abbr': {
		'title': re.compile(r'^[\w\s]+$'),
		'class': [
			'initialism'
		]
	},
	'address': {},
	'blockquote': {
		'class': [
			'pull-right'
		]
	},
	'cite': {
		'title': re.compile(r'^[\w\s]+$')
	},

	'li': {
		'class': [
			'span1',
			'span2',
			'span3',
			'span4',
			'span5',
			'span6',
			'span7',
			'span8',
			'span9',
			'span10',
			'span11',
			'span12'
		]
	},
	'ul': {
		'class': [
			'unstyled',
			'inline',

			'pager',
			'thumbnails',
			'media-list'
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
	'dl': {
		'class': [
			'dl-horizontal'
		]
	},

	'code': {},
	'pre': {
		'class': [
			'pre-scrollable'
		]
	},

	'table': {
		'class': [
			'table',
			'table-striped',
			'table-bordered',
			'table-hover',
			'table-condensed'
		]
	},
	'thead': {},
	'tbody': {},
	'tfoot': {},
	'tr': {
		'class': [
			'success',
			'error',
			'warning',
			'info'
		]
	},
	'td': {},
	'caption': {},

	'p': {
		'class': [
			'text-left',
			'text-center',
			'text-right',
			'muted',
			'text-warning',
			'text-error',
			'text-info',
			'text-success',
			'lead'
		]
	},

	# aliases
	'center': 'p class="text-center"',
	'script': 'code'
}
