import FilterHTML
import test1
import test2
import re

f = open('tests/test1.html', 'r')
html = f.read()
f.close()

f = open('tests/test1.out.html', 'r')
html_out = f.read()
f.close()

result = FilterHTML.filter_html(html, test1.SPEC)

assert html_out.strip() == result.strip()

f = open('tests/test2.html', 'r')
html = f.read()
f.close()

f = open('tests/test2.out.html', 'r')
html_out = f.read()
f.close()

result = FilterHTML.filter_html(html, test2.SPEC)

assert html_out.strip() == result.strip()

f = open('tests/test3.html', 'r')
html = f.read()
f.close()

f = open('tests/test3.out.html', 'r')
html_out = f.read()
f.close()

URLIZE_RE = '(%s)' % '|'.join([
    r'<(?:f|ht)tps?://[^>]*>',
    r'\b(?:f|ht)tps?://[^)<>\s]+[^.,)<>\s]',
])

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

result = FilterHTML.filter_html(html, test1.SPEC, text_filter=urlize, remove=['script', 'style'])

assert html_out.strip() == result.strip()

print 'All Tests Passed'

