import os
import re
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
import sys
from unidecode import unidecode

init()

class LWCLabelGenerator:
    def __init__(self, component_name, naming_style):
        self.component_name = component_name
        self.naming_style = naming_style
        self.component_path = f"force-app/main/default/lwc/{component_name}"
        self.label_path = f"force-app/main/default/labels/{component_name}"
        self.html_path = os.path.join(self.component_path, f"{component_name}.html")
        self.labels = {} 
        self.metrics = {
            'total_labels': 0,
            'button_labels': 0,
            'text_elements': 0
        }

        self.text_elements = ['p', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div', 'label', 'th', 'td']

        if not os.path.exists(self.label_path):
            os.makedirs(self.label_path)

    def print_status(self, message, status="info"):
        colors = {
            "success": Fore.GREEN,
            "error": Fore.RED,
            "info": Fore.BLUE,
            "warning": Fore.YELLOW
        }
        print(f"{colors[status]}\u2192 {message}{Style.RESET_ALL}")

    def validate_files(self):
        if not os.path.exists(self.component_path):
            self.print_status(f"Component directory not found: {self.component_path}", "error")
            return False
        
        if not os.path.exists(self.html_path):
            self.print_status(f"HTML file not found: {self.html_path}", "error")
            return False

        if os.path.exists(os.path.join(self.label_path, 'labels.js')):
            print(f"\n{Fore.CYAN}=== File already found ==={Style.RESET_ALL}\n")
            proceed = input(f"{Fore.CYAN}[?] A 'labels.js' file already exists for this component. Proceeding will make the content of this file be lost. Are you sure (y/n)? {Style.RESET_ALL}")
            return str.upper(proceed) == 'Y'
        
        return True

    def create_label_name(self, text, prefix=''):
        normalized_text = unidecode(text.strip())
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', normalized_text)
        words = clean_text.lower().split()
        if not words:
            return ''
        
        if prefix: words.insert(0, prefix)
        if self.naming_style == 'snake_case':
            label_name = '_'.join(words)
        elif self.naming_style == 'camelCase':
            label_name = words[0].lower() + ''.join(word.title() for word in words[1:])
        elif self.naming_style == 'PascalCase':
            label_name = ''.join(word.title() for word in words)
        elif self.naming_style == 'UPPER_CASE':
            label_name = str.upper('_'.join(words))
        else:
            raise ValueError("Unsupported naming style")

        return label_name

    def should_process_text(self, element):
        if re.match(r'{\s*.*\s*}', element.strip()):
            return False
        
        if not element.strip():
            return False
        
        if element.parent.name in ['script', 'style']:
            return False
            
        if (element.parent.name not in self.text_elements and 
            not (element.parent.name == 'lightning-button' and element.parent.get('label') == element.strip())):
            return False
            
        return True

    def process_html(self):
        with open(self.html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        for button in soup.find_all(['lightning-button', 'button']):
            label = button.get('label', '')
            if label and not re.match(r'{\s*.*\s*}', label):
                self.metrics['button_labels'] += 1
                label_name = self.create_label_name(label, 'btn')
                self.labels[label_name] = label
                button['label'] = f"{{label.{label_name}}}"

        for element in soup.find_all(string=True):
            if self.should_process_text(element):
                text = element.strip()
                self.metrics['text_elements'] += 1
                label_name = self.create_label_name(text)
                self.labels[label_name] = text

                element.replace_with(f"{{label.{label_name}}}")

        self.metrics['total_labels'] = len(self.labels)
        labeled_html_path = os.path.join(self.label_path, f"{self.component_name}.html")
        with open(labeled_html_path, 'w', encoding='utf-8') as file:
            content = soup.prettify(formatter=None)
            content = re.sub(r'="\{(.*?)\}"', r'={\1}', content)
            file.write(content)

        return labeled_html_path

    def generate_js_file(self):
        js_content = []
        labels = list(self.labels.keys())
        labels.sort()
        for label_name in labels:
            js_content.append(f"import {label_name} from '@salesforce/label/c.{label_name}';")
        
        js_content.append("\nexport const label = {")
        js_content.extend(f"    {name}," for name in labels)
        js_content.append("};")

        js_path = os.path.join(self.label_path, "labels.js")
        with open(js_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(js_content))
        return js_path

    def generate_xml_file(self):
        xml_content = ['<?xml version="1.0" encoding="UTF-8"?>', '<CustomLabels xmlns="http://soap.sforce.com/2006/04/metadata">']
        
        for label_name, raw_text in self.labels.items():
            label_xml = f"""    <labels>
        <fullName>{label_name}</fullName>
        <categories>{self.component_name}</categories>
        <language>en_US</language>
        <protected>false</protected>
        <shortDescription>{raw_text}</shortDescription>
        <value>{raw_text}</value>
    </labels>"""
            xml_content.append(label_xml)
        
        xml_content.append('</CustomLabels>')
        
        xml_path = os.path.join(self.label_path, "labels.xml")
        with open(xml_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(xml_content))
        return xml_path

def main():
    print(f"{Fore.CYAN}=== LWC Label Generator ==={Style.RESET_ALL}\n")
    
    component_name = input(f"{Fore.CYAN}[?] Enter LWC component name: {Style.RESET_ALL}")

    naming_style = ''
    naming_styles_map = {
        '1': 'camelCase',
        '2': 'snake_case',
        '3': 'PascalCase',
        '4': 'UPPER_CASE'
    }
 
    while naming_style not in naming_styles_map.keys():
        print(f"\n{Fore.CYAN}=== Choose label naming style ==={Style.RESET_ALL}\n")
        for key, style in naming_styles_map.items():
            print(f"[{key}] {style}")

        naming_style = input(f"\n{Fore.CYAN}[?] Your choice: {Style.RESET_ALL}").strip()

    naming_style = naming_styles_map[naming_style]

    generator = LWCLabelGenerator(component_name, naming_style)
    
    if not generator.validate_files():
        print(f"\n{Fore.CYAN}=== Generation Exited ==={Style.RESET_ALL}")
        sys.exit(1)

    generator.print_status("Starting label generation process...", "info")
    
    labeled_html_path = generator.process_html()
    js_path = generator.generate_js_file()
    xml_path = generator.generate_xml_file()

    print(f"\n{Fore.GREEN}=== Generation Complete ==={Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}[Metrics]\n{Style.RESET_ALL}")
    print(f"\u2022 Total labels created: {generator.metrics['total_labels']}")
    print(f"\u2022 Button labels: {generator.metrics['button_labels']}")
    print(f"\u2022 Text elements: {generator.metrics['text_elements']}")

    print(f"\n{Fore.CYAN}[Next Steps]{Style.RESET_ALL}")
    
    print(f"\n1. {Fore.YELLOW}JavaScript Labels File:{Style.RESET_ALL}")
    print(f"   \u2192 Location: {js_path}")
    print(f"   \u2192 Move to your component folder and import it in your main JS file using:")
    print(f"""\n     import {{ label }} from './labels';
     export default class YourLWCComponent extends LightningElement {{
         label = label;
     }}
    """)

    print(f"\n2. {Fore.YELLOW}Labeled HTML File:{Style.RESET_ALL}")
    print(f"   → Location: {labeled_html_path}")
    print(f"   → Replace your original HTML file with this one after importing the labels.js")
    
    print(f"\n3. {Fore.YELLOW}XML Labels File:{Style.RESET_ALL}")
    print(f"   → Location: {xml_path}")
    print(f"   → Append contents to: force-app/main/default/labels/CustomLabels.labels-meta.xml")
    print(f"   → If the labels file doesn't exist, add to package.xml:")
    print(f"""     <types>
        <members>*</members>
        <name>CustomLabels</name>
    </types>""")
    print(f"   → More info: https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/manifest_samples.htm\n")

if __name__ == "__main__":
    main()
