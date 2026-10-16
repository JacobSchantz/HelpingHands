import re, sys, collections
t = open(sys.argv[1]).read()
# split footprints
fps = re.split(r'\n\t\(footprint ', t)[1:]
nets = collections.defaultdict(list)
for fp in fps:
    ref = re.search(r'\(property "Reference" "([^"]+)"', fp)
    val = re.search(r'\(property "Value" "([^"]+)"', fp)
    ref = ref.group(1) if ref else "?"
    for m in re.finditer(r'\(pad "([^"]*)"[^\n]*?(?:\n[^\n]*?){0,12}?\(net (\d+) "([^"]*)"\)', fp):
        pass
    for pad in re.finditer(r'\(pad "([^"]*)"(.*?)\n\t\t\)', fp, re.S):
        n = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', pad.group(2))
        pf = re.search(r'\(pinfunction "([^"]*)"\)', pad.group(2))
        if n: nets[n.group(1)].append(f"{ref}.{pad.group(1)}" + (f"({pf.group(1)})" if pf else ""))
    print(ref, val.group(1) if val else "")
print()
for k in sorted(nets): print(f"{k:30s} {' '.join(nets[k])}")
