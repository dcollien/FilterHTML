import FilterHTML
import test1
import test2

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
