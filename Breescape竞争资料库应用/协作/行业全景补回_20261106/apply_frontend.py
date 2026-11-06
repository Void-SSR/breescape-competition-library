import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
target=ROOT/'static/industry.js'
s=target.read_text()
blocks=re.split(r'^// REPLACE (\w+)\n',Path(__file__).with_name('panorama_functions.js').read_text(),flags=re.M)
for name,body in zip(blocks[1::2],blocks[2::2]):
 pattern=r'^function '+name+r'\(.*?(?=^function |\nlet atlasPrintState)'
 s,n=re.subn(pattern,lambda match:body.strip()+'\n',s,count=1,flags=re.M|re.S)
 if n!=1:raise ValueError(name)
# Growth remains structured data but no longer a standalone page renderer.
s=re.sub(r'^function atlasGrowth\(.*?(?=^function )','',s,flags=re.M|re.S)
target.write_text(s)
print('frontend functions updated')
