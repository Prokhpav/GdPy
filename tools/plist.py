import xml.etree.ElementTree as ET

def xml_elem(tag, text=None, children=None, attrs=None):
    elem = ET.Element(tag, attrs if attrs else {})
    if text:
        elem.text = text
    if children:
        elem.extend(children)
    return elem

def _xml_to_json(element: ET.Element):
    if element.tag in ('t', 'true'):
        return True
    if element.tag in ('f', 'false'):
        return False
    if element.tag in ('s',):
        return element.text if element.text is not None else ''
    if element.tag in ('i',):
        return int(element.text)
    if element.tag in ('r',):
        return float(element.text)

    if element.tag not in ('d', 'dict'):
        raise ValueError(element.tag)
    children = iter(element)
    d = {key_elem.text: _xml_to_json(val_elem) for key_elem, val_elem in zip(children, children, strict=True)}
    if not d.get('_isArr', False):
        return d
    return [d[f'k_{i}'] for i in range(len(d) - 1)]

def _json_to_xml(value):
    if isinstance(value, bool):
        return xml_elem('ft'[value])
    if isinstance(value, str):
        return xml_elem('s', value)
    if isinstance(value, int):
        return xml_elem('i', str(value))
    if isinstance(value, float):
        return xml_elem('r', str(value))
    if isinstance(value, list):
        value = {'_isArr': True} | {f'k_{i}': v for i, v in enumerate(value)}

    if not isinstance(value, dict):
        raise TypeError()
    children = []
    for k, v in value.items():
        children.append(xml_elem('k', k))
        children.append(_json_to_xml(v))
    return xml_elem('d', children=children)

def plist_to_json(data: bytes):
    xml_etree = ET.ElementTree(ET.fromstring(data))
    plist_root = xml_etree.getroot()[0]
    json_data = _xml_to_json(plist_root)
    return json_data

def json_to_plist(json_data: dict) -> bytes:
    xml_data = _json_to_xml(json_data)
    xml_data.tag = 'dict'
    root = xml_elem(
        'plist', attrs={'version': '1.0', 'gjver': '2.0'}, children=[xml_data]
    )
    data = '<?xml version="1.0"?>' + ET.tostring(root, encoding='unicode')
    return data.encode('utf-8')
