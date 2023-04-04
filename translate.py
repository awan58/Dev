import boto3

# Add your access key and secret access key below
ACCESS_KEY = 'public'
SECRET_ACCESS_KEY = 'secret'
REGION = 'us-west-2' # replace with the appropriate region for your case

# Create an instance of the Amazon Translate client with your access key and secret access key
translate = boto3.client(
    service_name='translate',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_ACCESS_KEY,
    region_name=REGION  
)

# Function to load translations from a file
def load_translations(filename):
    translations = {}
    with open(filename, encoding="utf-8") as f:
        header = {}
        translations_list = []
        current_translation = {}
        in_header = False
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("sml"):
                continue
            elif line.startswith("localization"):
                continue
            elif line.startswith("header"):
                in_header = True
            elif line.startswith("translations"):
                in_header = False
            elif in_header:
                key, value = line.split("=")
                header[key.strip()] = value.strip()
            else:
                current_key = ""
                current_value = ""
                for i in range(len(line)):
                    if line[i] == "=":
                        current_key = line[0:i].strip()
                        current_value = line[i+1:].strip()
                        break
                current_translation[current_key] = current_value
            if current_translation and not in_header:
                translations_list.append(current_translation)
                current_translation = {}
        if current_translation and not in_header:
            translations_list.append(current_translation)
            
        # Truncate source_lang and target_lang to 5 characters if necessary
        header["source_lang"] = header.get("source_lang", "")[:5]
        header["target_lang"] = header.get("target_lang", "")[:5]
        translations["header"] = header
        translations["translations"] = translations_list
    return translations

# Function to write translations to a file
def write_translations(filename, translations_dict, indentation_level=0):
    header = translations_dict["header"]
    translations = translations_dict["translations"]
    output = "sml = version = 0.1; encoding = utf-8\n"
    output += "localization\n"
    output += "header\n"
    for key, value in header.items():
        output += f"{key} = {value}\n"
    output += "translations\n"
    for translation in translations:
        output += "unit\n"
        for key, value in translation.items():
            if key == "target":
                output += f"{indentation_level * '    '}{key} = {value}\n"
            else:
                output += f"{indentation_level * '    '}{key} = \n"
                output += write_translations("", {"translations": value}, indentation_level + 1)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output)
    return output


# Load translations from the input file
translations_dict = load_translations("langs/urdu.local")

# Get source and target language
header = translations_dict["header"]
source_lang = header.get("source_lang", "")[:5]
target_lang = header.get("target_lang", "")[:5]
translations = translations_dict["translations"]

# Translate each source field to target field
for translation in translations:
    if "source" in translation:
        source_text = translation["source"].strip()
        target_text = translate.translate_text(Text=source_text, SourceLanguageCode=source_lang, TargetLanguageCode=target_lang)['TranslatedText']
        translation["target"] = target_text

# Write the translated file
write_translations("langs/urdu_translated.local", translations_dict)