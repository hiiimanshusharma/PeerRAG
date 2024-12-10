from tqdm import tqdm
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from transformers import pipeline
from langchain.embeddings import HuggingFaceEmbeddings

def load_and_process_data(file_path):
    """Load and process data with improved error handling."""
    try:
        data = json.loads(Path(file_path).read_text())
        texts = []
        for company in tqdm(data):
            try:
                company_name = company["company_name"]
                company_description = company.get("company_description", "")
                location = company.get("location", "")
                website = company.get("website", "")
                
                for person in company.get("people", []):
                    text_to_embed = process_person_data(person, company_name, location, website, company_description)
                    texts.append(text_to_embed)
            except KeyError as e:
                print(f"Missing key in company data: {e}")
        
        return texts
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

def process_person_data(person, company_name, location, website, company_description):
    """Process individual person's data."""
    name = person.get("name", "")
    position = person.get("position", "")
    profile_uri = person.get("profile_uri", "")
    
    education = person.get("resume", {}).get("Education", [])
    experience = person.get("resume", {}).get("Experience", {})
    links = person.get("resume", {}).get("links", [])
    
    education_details = ', '.join([
        f"{edu.get('course_name', '')} at {edu.get('institute_name', '')} ({edu.get('course_duration', '')})"
        for edu in education
    ])
    
    experience_details = ', '.join([
        f"{exp.get('role', '')} at {exp.get('company_name', '')} ({exp.get('exp_duration', '')})"
        for exp in experience.get("companies", [])
    ])
    
    link_details = ', '.join([f"{link.get('link_name', '')}: {link.get('link_url', '')}" for link in links])
    
    text_to_embed = (
        f"{name} works as {position} at {company_name}, located in {location}. "
        f"Company website: {website}. Profile: {profile_uri}. "
        f"Education: {education_details}. Experience: {experience_details}. "
        f"Links: {link_details}. Company Description: {company_description}."
    )
    
    return text_to_embed

def create_vector_store(texts):
    """Create vector store from processed texts."""
    # Use HuggingFaceEmbeddings to wrap the SentenceTransformer
    embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
    
    documents = [Document(page_content=text) for text in texts]
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    return vectorstore

def format_docs(documents):
    """Format the documents by extracting their content."""
    return "\n\n".join(doc.page_content for doc in documents)

def setup_rag_system(file_path):
    """Set up the entire RAG system."""
    texts = load_and_process_data(file_path)
    vectorstore = create_vector_store(texts)
    retriever = vectorstore.as_retriever()
    
    prompt_template = """Use the context below to answer the question:
    Context:
    {context}
    Question:
    {question}
    Answer:"""
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    qa_pipeline = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        device=-1  # Set to -1 for CPU
    )
    
    def rag_chain(question):
        retrieved_docs = retriever.invoke(question)
        context = format_docs(retrieved_docs)
        formatted_prompt = prompt.format(context=context, question=question)
        response = qa_pipeline(formatted_prompt, max_length=200, do_sample=False)
        return response[0]['generated_text']
    
    return rag_chain

# Usage
file_path = './data/master_data/companies_people_resume.json'
rag_chain = setup_rag_system(file_path)
result = rag_chain("Who is the most experienced person?")
print(result)