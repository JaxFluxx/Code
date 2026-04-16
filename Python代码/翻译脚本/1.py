import argostranslate.package, argostranslate.translate
from urllib.request import urlopen

# 下载中文 <-> 英文翻译包
url = "https://www.argosopentech.com/argospm/packages/translate-en_zh.argosmodel"
package_path = "translate-en_zh.argosmodel"
with open(package_path, "wb") as f:
    f.write(urlopen(url).read())
argostranslate.package.install_from_path(package_path)
