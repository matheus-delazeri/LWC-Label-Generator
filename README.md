# LWC Label Generator

The **LWC Label Generator** is a Python script designed to automate the generation of custom labels for Salesforce Lightning Web Components (LWCs). It processes the HTML of a specified LWC component, identifies text and button labels, and generates the necessary resources, including:

- A labeled HTML file
- A JavaScript file for importing labels
- An XML file for integrating custom labels with Salesforce metadata
- Choosing label case from: camelCase, snake_case, PascalCase and UPPER_CASE

## Features

- Extracts and replaces static text and button labels with Salesforce-compatible label references.
- Generates a `labels.js` file to simplify the import of custom labels into your LWC components.
- Outputs a Salesforce-compatible `CustomLabels.labels-meta.xml` file for easy integration into your project.

---

## Getting Started

### Prerequisites

- **Python 3.6+** installed on your system.
- The following Python libraries:
  - `beautifulsoup4`
  - `unidecode`
  - `colorama`

You can install the dependencies with the following command:

```bash
pip install beautifulsoup4 unidecode colorama
```

## Installation

1. Clone the repository or download the script file:
```
git clone https://github.com/matheus-delazeri/lwc-label-generator.git
cd lwc-label-generator
```
2. Place the script in the root directory of your Salesforce project.

## Usage

1. Run the script
```
python lwc_label_generator.py
```
2. Enter the name of your Lightning Web Component when prompted. The script expects your component to be located in the following path:
```
force-app/main/default/lwc/<component_name/
```
3. Follow the prompts to generate the labeled files. The script will:
- Validate the component directory and HTML file.
- Create or replace the `labels.js` file and labeled HTML file in `force-app/main/default/labels/<component_name/`.
- Generate the `labels.xml` file.

## Output

The script generates the following files:

1. JavaScript Labels File

- **Location:** `force-app/main/default/labels/<component_name>/labels.js`
- Move the file to your component's folder and import it in your LWC JavaScript file

2. Labeled HTML File
- **Location:** `force-app/main/default/labels/<component_name>/<component_name>.html`
- Replace the original HTML file with the newly generated labeled HTML file.

3. XML Labels File
- **Location:** `force-app/main/default/labels/<component_name>/labels.xml`
- Append the contents of this file to `CustomLabels.labels-meta.xml`

## Example Output

### Original HTML
```html
<h1>Welcome to our App</h1>
<button label="Click Me"></button>
```
### Labeled HTML
```html
<h1>{label.welcomeToOurApp}</h1>
<button label={label.btnClickMe}></button>
```
### JavaScript File
```js
import welcomeToOurApp from '@salesforce/label/c.welcomeToOurApp';
import btnClickMe from '@salesforce/label/c.btnClickMe';

export const label = {
    welcomeToOurApp,
    btnClickMe,
};
```
### XML File
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomLabels xmlns="http://soap.sforce.com/2006/04/metadata">
    <labels>
        <fullName>welcomeToOurApp</fullName>
        <categories>YourComponentName</categories>
        <language>en_US</language>
        <protected>false</protected>
        <shortDescription>Welcome to our App</shortDescription>
        <value>Welcome to our App</value>
    </labels>
    <labels>
        <fullName>btnClickMe</fullName>
        <categories>YourComponentName</categories>
        <language>en_US</language>
        <protected>false</protected>
        <shortDescription>Click Me</shortDescription>
        <value>Click Me</value>
    </labels>
</CustomLabels>
```
