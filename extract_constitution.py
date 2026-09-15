import fitz

pdf_path = "raw/constitution/Constitution_of_India_2024.pdf"

doc = fitz.open(pdf_path)

text = ""

for page in doc:
    text += page.get_text() + "\n"

with open("constitution_raw.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Extraction complete!")
print("Pages:", len(doc))
print("Characters:", len(text))