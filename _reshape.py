import re, pathlib
root = pathlib.Path(".")
NAV = '''<nav id="site-nav" class="site-nav" aria-label="Main">
      <a href="index.html"{h}>Home</a>
      <a href="about.html"{a}>About</a>
      <a href="books.html"{bk}>Books</a>
      <a href="testing.html"{t}>Testing &amp; Reports</a>
      <a href="blog/index.html">Blog</a>
      <a href="contact.html"{c}>Contact</a>
      <details class="shop-menu">
        <summary>Shop</summary>
        <div class="shop-list">
          <a href="https://labs.rupahealth.com/store/storefront_nYeZEmn" rel="noopener">Shop Labs</a>
          <a href="https://us.fullscript.com/welcome/iconic/store-start" rel="noopener">Shop Supplements</a>
        </div>
      </details>
      <a class="btn btn-gold" href="book.html#free-chapter">Read a free chapter</a>
    </nav>'''
pages = ["index.html","about.html","book.html","services.html","training.html",
         "contact.html","faq.html","testimonials.html","privacy.html","join-pma.html","404.html"]
navrx = re.compile(r'<nav id="site-nav".*?</nav>', re.S)
cons = '<li><a href="https://go.oncehub.com/HealthConsultation" rel="noopener">Book a consultation</a></li>'
bookli = '<li><a href="book.html">Bad Medicine Blues — the book</a></li>'
for name in pages:
    f = root/name
    if not f.exists(): 
        print("skip (missing)", name); continue
    s = f.read_text()
    d = {"h":"","a":"","bk":"","t":"","c":""}
    k = {"index.html":"h","about.html":"a","contact.html":"c"}.get(name)
    if k: d[k] = ' aria-current="page"'
    s2, n = navrx.subn(NAV.format(**d), s, count=1)
    s2 = s2.replace("\n          "+cons, "").replace(cons, "")
    if bookli in s2:
        s2 = s2.replace(bookli, bookli + '\n          <li><a href="testing.html">Testing &amp; Reports</a></li>')
    f.write_text(s2)
    print(f"updated {name}  (nav replaced: {n})")
