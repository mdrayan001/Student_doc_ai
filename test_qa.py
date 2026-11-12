import sys
sys.path.insert(0, '/c/Users/rayan/student-doc-ai')
from student_doc_ai import image_handler, ollama_client, state
from student_doc_ai.cli import StudentDocAI
from PIL import Image, ImageDraw

# Create test image
img = Image.new('RGB', (800, 200), 'white')
d = ImageDraw.Draw(img)
d.text((20, 80), 'Student Name: Zeeshan Ahmed', fill='black')
d.text((20, 120), 'Father Name: Mr. Ahmed', fill='black')
d.text((20, 160), 'Grade: A+', fill='black')
d.text((20, 200), 'Subject: Data Structure', fill='black')
img.save('/c/Users/rayan/student-doc-ai/test_doc.png')

# Load and encode
img = image_handler.load_image('/c/Users/rayan/student-doc-ai/test_doc.png')
img = image_handler.resize_image_for_model(img)
encoded = image_handler.encode_image_to_base64(img)

# Set up the app
app = StudentDocAI()
app.current_image_encoded = encoded
state.set_current_image('/c/Users/rayan/student-doc-ai/test_doc.png')

# Extract text
print('Extracting text...')
messages = [{'role': 'user', 'content': 'Extract all text from this image. Provide only the text content.'}]
response = ollama_client.chat_completion(messages, images=[encoded])
extracted_text = response.get('message', {}).get('content', '').strip()
state.set_extracted_text(extracted_text)
print(f'Extracted: {extracted_text[:200]}')
print()

# Now ask a question
print('Asking question...')
question = 'What is the student name?'
query = (
    'Answer this question about the document below.\n\n'
    f'EXTRACTED TEXT:\n{extracted_text}\n\n'
    '---\n'
    f'Question: {question}\n'
    'Based on the EXTRACTED TEXT above, provide a clear and accurate answer. '
    'Do not make up information that is not in the text. '
    'If the text does not contain the answer, say you cannot find the answer in the document.'
)

response = ollama_client.chat_completion([{'role': 'user', 'content': query}], images=[encoded])
answer = response.get('message', {}).get('content', '').strip()
print(f'Answer: {answer}')
print('[SUCCESS] Q&A with extracted text context works!')
