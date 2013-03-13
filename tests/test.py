import FilterHTML
import test1

f = open('tests/test1.html', 'r')
html = f.read()
f.close()

f = open('tests/test1.out.html', 'r')
html_out = f.read()
f.close()

result = FilterHTML.filter_html(html, test1.SPEC)

assert html_out.strip() == result.strip()
