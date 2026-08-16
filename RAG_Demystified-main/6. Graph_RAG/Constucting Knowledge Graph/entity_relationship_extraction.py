from openai import OpenAI


# ============================================================================
# SETUP: Import LLM Helper Functions
# ============================================================================
# We use helper functions to create LLM instances with proper configuration
# These functions handle API key loading and model configuration

import os
import sys

# Add parent directory to path for importing helpers
sys.path.append(os.path.abspath(".."))

# Import our LLM factory functions
# - get_groq_llm(): Creates a Groq-hosted LLM (fast inference)
# - get_openai_llm(): Creates an OpenAI GPT model
from helpers.utils import get_groq_llm, get_openai_llm,get_databricks_llm

print("LLM helpers imported successfully!")

# ============================================================================
# CREATE THE LLM AND CHATBOT GRAPH
# ============================================================================

# -----------------------------------------------------------------------------
# Step 1: Initialize the LLM
# We use Groq for fast inference, but you can swap to OpenAI
# -----------------------------------------------------------------------------
llm = get_databricks_llm("databricks-gemini-2-5-pro")  # Fast, open-source models hosted by Groq
# Alternative: llm = get_openai_llm()  # OpenAI's GPT models

if hasattr(llm, 'model_name'):
    print(f"LLM initialized: {llm.model_name}")
elif hasattr(llm, 'model'):
    print(f"LLM initialized: {llm.model} (Databricks)")
else:
    print("LLM initialized: Groq LLM")


def convert_to_chunks(file_path, max_words_per_chunk):
  chunks = []
  current_chunk = []
  current_word_count = 0
    
  with open(file_path, "r") as file:
    for line in file:
      words = line.split()
      current_word_count += len(words)
      if current_word_count < max_words_per_chunk:
        current_chunk.append(line.strip())
      else:
        chunks.append(' '.join(current_chunk))
        current_chunk = []
        current_word_count = 0
        current_word_count += len(words)
        current_chunk.append(line.strip())
    
    # Add any remaining text in the last chunk
    if current_chunk:
      chunks.append(' '.join(current_chunk))
    print("\nChunks created.\n")
    return chunks

def extract_entities_relationships(text):
    messages = [
    {"role": "system", "content": """"
    You are a helper tool for a knowedge graph builder application. Your task is to extract entities and relationships from the text provided by the user. 
    Format the output in such a way that it can be directly parsed into Python lists. 
    The format should include:
    
    1. A list of **Entities** in Python list format.
    2. A list of **Relationships**, where each relationship is represented as a tuple in the format: (Entity 1, "Relationship", Entity 2).
    
    Here is the format to follow:
    
    Entities: ["Entity 1", "Entity 2", ..., "Entity N"]
    
    Relationships: [("Entity 1", "Relationship", "Entity 2"), ..., ("Entity X", "Relationship", "Entity Y")]
    
    Example Input:
    Extract entities and relationships from the following text:
    "Michael Jackson, born in Gary, Indiana, was a famous singer known as the King of Pop. He passed away in Los Angeles in 2009."
    
    Expected Output:
    
    Entities: ["Michael Jackson", "Gary, Indiana", "Los Angeles", "singer", "King of Pop", "2009"]
    
    Relationships: [
      ("Michael Jackson", "born in", "Gary, Indiana"), 
      ("Michael Jackson", "profession", "singer"), 
      ("Michael Jackson", "referred to as", "King of Pop"), 
      ("Michael Jackson", "passed away in", "Los Angeles"), 
      ("Michael Jackson", "date of death", "2009")
    ]
    """},
    {"role": "user", "content": f"Extract entities and relationship tuples from the following text:\n\n{text}\n\n"}
    ]
  
    response = llm.invoke(messages)
    response_content = response.content
    return response_content

import ast
def parse_llm_response_content(content):
    """
    Parse the LLM output to extract entities and relationships.
    """
    entity_section = content.split("Entities:")[1].split("Relationships:")[0].strip()
    relationship_section = content.split("Relationships:")[1].strip()

    entities = ast.literal_eval(entity_section)
    relationships = ast.literal_eval(relationship_section)
    
    return entities, relationships

def get_entities_relationships(file_path, wordsPerChunk=2665):
    """
    Chunk the input text, process each chunk, and combine results.
    """
    chunks = convert_to_chunks(file_path, wordsPerChunk)
    all_entities = []
    all_relationships = []
    i=1
    print("Number of chunks: ", len(chunks))
    for chunk in chunks:
        # Extract entities and relationships for each chunk
        content = extract_entities_relationships(chunk)
        print("Entities and realtionships have been extracted successfully for chunk ", i, ".\n")
        entities, relationships = parse_llm_response_content(content)
        print("Entities and realtionships have been parsed successfully for chunk ", i, ".\n")
        i=i+1
        # Aggregate entities and relationships
        all_entities.extend(entities)
        all_relationships.extend(relationships)
    
    # Remove duplicates from entities
    all_entities = list(set(all_entities))
    print("All entities and realtionships have been extracted successfully.")
    return all_entities, all_relationships