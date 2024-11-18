from bs4 import BeautifulSoup

html_content = """<html>
<head>
<title>My first web page</title>
</head>
<body>
<h1>My first web page</h1>
<h2>What this is tutorial</h2>
<p>A simple page put together using HTML. <em>I said a simple page.</em>.</p>
<ul>
 <li>To learn HTML</li>
 <li>
 To show off
 <ol>
Grammar (CFG):
S → NP VP
NP → Det Nominal
Nominal → Nominal Noun | Noun
VP → V NP | V
Det → 'the' | 'a'
Noun → 'dog' | 'park' | 'chase'
V → 'sees' | 'finds'
Lexicon:
Det (Determiner): the, a
Noun: dog, park, chase
V (Verb): sees, finds
 <li>To my boss</li>
 <li>To my friends</li>
 <li>To my cat</li>
 <li>To the little talking duck in my brain</li>
 </ol>
 </li>
 <li>Because I have fallen in love with my computer and want to give her some HTML loving.</li>
</ul>
<h3>Where to find the tutorial</h3>
<p><a href="http://www.aaa.com"><img src=http://www.aaa.com/badge1.gif></a></p>
<h4>Some random table</h4>
<table>
 <tr class="tutorial1">
 <td>Row 1, cell 1</td>
 <td>Row 1, cell 2<img src=http://www.bbb.com/badge2.gif></td>
 <td>Row 1, cell 3</td>
 </tr>
 <tr class="tutorial2">
 <td>Row 2, cell 1</td>
 <td>Row 2, cell 2</td>
 <td>Row 2, cell 3<img src=http://www.ccc.com/badge3.gif></td>
 </tr>
</table>
</body>
</html>"""

soup = BeautifulSoup(html_content, "html.parser")

# a
print("a. Page Title:", soup.title.text)

# b
print("b. Second <li> under 'To show off':", soup.find_all('li')[2].text)

# c
print("c. All <td> tags in the first <tr> of the table:")
for td in soup.find("tr", class_="tutorial1").find_all("td"):
    print(td.text)

# d
print("d. <h2> heading containing 'tutorial':", soup.find("h2", string=lambda s: "tutorial" in s.lower()).text)

# e
print("e. All text containing 'HTML':")
for s in soup.find_all(string=lambda t: "HTML" in t):
    print(s.strip())

# f
print("f. All text in the second <tr> row:")
for td in soup.find("tr", class_="tutorial2").find_all("td"):
    print(td.text)

# g
print("g. All <img> tags from the table:")
for img in soup.table.find_all("img"):
    print(img["src"])
