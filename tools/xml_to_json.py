import json
import asyncio
import xml.etree.ElementTree as ET
from tools.utils import yield_log, yield_error, yield_success

def xml_to_dict(element):
    d = {element.tag: {} if element.attrib else None}
    children = list(element)
    if children:
        dd = {}
        for dc in map(xml_to_dict, children):
            for k, v in dc.items():
                if k in dd:
                    if not isinstance(dd[k], list):
                        dd[k] = [dd[k]]
                    dd[k].append(v)
                else:
                    dd[k] = v
        d = {element.tag: dd}
    if element.attrib:
        d[element.tag].update(('@' + k, v) for k, v in element.attrib.items())
    if element.text:
        text = element.text.strip()
        if children or element.attrib:
            if text:
                d[element.tag]['#text'] = text
        else:
            d[element.tag] = text
    return d

async def run(params: dict):
    xml_str = params.get("xml", "").strip()
    if not xml_str:
        yield yield_error("XML input string is required.")
        return
        
    yield yield_log("Parsing XML structure...")
    
    try:
        root = ET.fromstring(xml_str)
        res_dict = xml_to_dict(root)
        out = json.dumps(res_dict, indent=4)
        yield {"type": "found", "message": out}
        yield yield_success("XML converted successfully.")
    except Exception as e:
        yield yield_error(f"XML parsing failed: {str(e)}")
