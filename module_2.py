import re
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from config import GROQ_API_KEY

# Map for converting superscripts if needed
superscript_map = {
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'
}

# Function to convert superscripts (if applicable)
def convert_superscript(text):
    # Regular expression to find any number or character followed by superscript digits
    pattern = re.compile(r'(\w+)([⁰¹²³⁴⁵⁶⁷⁸⁹]+)')
    
    def replace(match):
        base = match.group(1)  # The main number or character
        superscript_digits = match.group(2)  # The superscript digits
        
        # Convert superscript digits to regular digits
        exponent = ''.join(superscript_map[digit] for digit in superscript_digits)
        
        # Return the formatted result
        return f'{base} to the power of {exponent}'
    
    # Replace all occurrences
    return pattern.sub(replace, text)

# Pattern to match a character/number followed by '^' and another character/number
power_pattern = re.compile(r'(\w+)\^(\w+)')

# Function to convert power notation like a^2 or 2^a
def convert_power_notation(text):
    def replace(match):
        base = match.group(1)  # The base (letter or number)
        exponent = match.group(2)  # The exponent (letter or number)
        return f'{base} to the power of {exponent}'
    
    return power_pattern.sub(replace, text)

# Model and prompt template
model = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY)

prompt = """
    The conversation so far:
    {history}

    As an expert in question answering, provide a concise and precise answer to the following question: {question}
    Please keep your response as short as possible and focused. The answer should be in one or two sentences maximum.
    """

template = PromptTemplate(template=prompt, input_variables=["history", "question"])
memory = ConversationBufferMemory(limit=2)

# Main function for processing text
def text_to_text(question):
    chain = LLMChain(llm=model, prompt=template, memory=memory, verbose=True)
    response = chain(question)
    text = response['text'].strip()

    # Replace various symbols with words
    text_with_replacements = re.sub(r'(?<=\d|s)-(?=\d|s)', ' to ', text)
    text_with_replacements = text_with_replacements.replace('!', '').replace('(', '').replace(')', '')
    text_with_replacements = text_with_replacements.replace('mph', 'miles per hour').replace('kph', 'kilometers per hour')
    text_with_replacements = text_with_replacements.replace('mps', 'miles per second').replace('kps', 'kilometers per second')
    text_with_replacements = text_with_replacements.replace('/s', 'per second').replace('/h', 'per hour').replace('e.g.','example given')
    text_with_replacements = text_with_replacements.replace('km', ' kilometers ').replace('=', ' equals ').replace('π', ' pie ').replace('pi','pie')
    
    # Convert superscript notations (if needed)
    text_with_replacements = convert_superscript(text_with_replacements)
    
    # Convert power notation like a^2 or 2^a
    text_with_replacements = convert_power_notation(text_with_replacements)
    
    return text_with_replacements
