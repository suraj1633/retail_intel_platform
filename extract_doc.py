import zipfile
import xml.etree.ElementTree as ET

docpath = r"c:\Users\suraj\Downloads\Project Brief Multi Brand Comparison.docx"
with zipfile.ZipFile(docpath, 'r') as zip_ref:
    xml_content = zip_ref.read('word/document.xml')

root = ET.fromstring(xml_content)

# Extract all text from the document
def extract_text(element):
    text = []
    for elem in element.iter():
        if elem.tag.endswith('}t'):
            if elem.text:
                text.append(elem.text)
        elif elem.tag.endswith('}br'):
            text.append('\n')
    return ''.join(text)

content = extract_text(root)
print(content)
