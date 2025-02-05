import os
import json
import uuid
import tempfile
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_pdf_text(pdf_files):
    text = ""
    for pdf_path in pdf_files:
        try:
            pdf_reader = PdfReader(pdf_path)
            for page in pdf_reader.pages:
                text += page.extract_text()
        except Exception as e:
            raise Exception(f"Error processing file {pdf_path}: {str(e)}")
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    Answer the question based on the context provided:
    Context: {context}
    Question: {question}
    Answer:
    """
    
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    
    return chain

def process_question(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    if not os.path.exists("faiss_index"):
        raise Exception("FAISS index not found. Process PDFs first.")
    
    try:
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
    except ValueError as e:
        raise Exception(f"Error loading FAISS index: {str(e)}")

    chain = get_conversational_chain()

    try:
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        return response["output_text"]
    except Exception as e:
        raise Exception(f"Error generating response: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def upload_files(request):
    try:
        files = request.FILES.getlist('files')
        if not files:
            return JsonResponse({'error': 'No files provided'}, status=400)

        saved_files = []
        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                for file in files:
                    if file.name.lower().endswith('.pdf'):
                        filepath = os.path.join(tmpdirname, file.name)
                        with open(filepath, 'wb+') as destination:
                            for chunk in file.chunks():
                                destination.write(chunk)
                        saved_files.append(filepath)

                raw_text = get_pdf_text(saved_files)
                if not raw_text:
                    return JsonResponse({'error': 'No text extracted from PDF files'}, status=400)

                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)

                return JsonResponse({'message': 'Files processed successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ask_question(request):
    try:
        data = json.loads(request.body)
        if not data or 'question' not in data:
            return JsonResponse({'error': 'No question provided'}, status=400)

        try:
            answer = process_question(data['question'])
            return JsonResponse({'answer': answer}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)