import json
from pymongo import MongoClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain.chains.question_answering import load_qa_chain
from langchain.schema import Document
from langchain.prompts import PromptTemplate
import env  # Ensure key_param contains MongoDB URI and Google API key

google_api_key = env.GOOGLE_API_KEY

# Load data from JSON file
def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# Convert JSON entries to Document format for embeddings
def json_to_documents(data):
    documents = []
    for entry in data:
        # Extract key fields to create a full text for embedding
        title = entry.get("title", "")
        chalet_title = entry.get("chalet_title", "")
        description = entry.get("description", "")
        chalet = entry.get("chalet", {})
        chalet_title_full = chalet.get("title", "")
        address_city = chalet.get("address", {}).get("city", "")
        address_area = chalet.get("address", {}).get("area", "")
        total_review_points = chalet.get("totalReview", {}).get("points", "")
        total_review_text = chalet.get("totalReview", {}).get("text", "")
        cancel_policy = chalet.get("cancelPolicy", "")
        unit_custom_title = entry.get("unit_custom_title", "")
        checkin_hour = entry.get("checkinHour", "")
        checkout_hour = entry.get("checkoutHour", "")
        final_price = entry.get("final_price", "")
        
        extra_description = entry.get("extraDescription", [])
        extra_description_text = "\n".join(
            [f"{desc['header']}: {', '.join(desc['content'])}" for desc in extra_description]
        )
        
        full_text = (
            f"{title}\n"
            f"{chalet_title}\n"
            f"{description}\n"
            f"{chalet_title_full}\n"
            f"{address_city}\n"
            f"{address_area}\n"
            f"التقييم: {total_review_points}\n"
            f"اجمالي التقييم: {total_review_text}\n"
            f"شروط الغاء الحجز: {cancel_policy}\n"
            f"{unit_custom_title}\n"
            f"تسجيل دخول: {checkin_hour}\n"
            f"تسجيل خروج: {checkout_hour}\n"
            f"السعر: {final_price}\n"
            f"{extra_description_text}"
        )
        
        # Create Document object with text and metadata
        documents.append(Document(page_content=full_text, metadata=entry))
    return documents


# MongoDB setup
client = MongoClient(env.MONGO_URI)
db = "riyadhMap"
collectionName = "mapData"
collection = client[db][collectionName]

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)

# NOTE: the following code used to load data from JSON file and create a vector store. 
# data = load_data("data.json")
# documents = json_to_documents(data)
# vectorStore = MongoDBAtlasVectorSearch.from_documents(documents, embeddings, collection=collection)


vectorStore = MongoDBAtlasVectorSearch(collection, embeddings)

# Language Model for RetrievalQA
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)

prompt_template = """
As a friendly tourism agent, suggest the best possible options based on the client's input. Your answer should be based on the text input language but mostly in Arabic or English. If there is no exact match, provide the top three closest possible information. Each context will provide `title` (e.g. كود الوحدة (xxxxx)), therefore, always include `title` in your answer for better user experience from the `context`. Be convincing and friendly in your response and use Saudi accent if the text in Arabic.\n\n
Context:\n{context}\n
Question:\n{question}\n
Answer:
"""

prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# Use the custom prompt with RetrievalQA to guide the model
retriever = vectorStore.as_retriever()
qa = load_qa_chain(llm, chain_type="stuff", prompt=prompt)

# Define a query function for vector-based similarity search and RAG
def query_data(query):
    # Perform similarity search
    docs = vectorStore.similarity_search(query, k=10)  # Increase the number of retrieved documents
    
    # Join document content for RAG context
    context = "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant documents found."
    properties = []
    for doc in docs:
        metadata = doc.metadata
        details = {
            "title": metadata.get("title", ""),
            "chalet_title": metadata.get("chalet_title", ""),
            "final_price": metadata.get("final_price", ""),
            "address": metadata.get("chalet", {}).get("address", {}).get("city", ""),
            "area": metadata.get("chalet", {}).get("address", {}).get("area", ""),
            "total_review_points": metadata.get("chalet", {}).get("totalReview", {}).get("points", ""),
            "total_review_text": metadata.get("chalet", {}).get("totalReview", {}).get("text", ""),
            "cancel_policy": metadata.get("chalet", {}).get("cancelPolicy", ""),
            "unit_custom_title": metadata.get("unit_custom_title", ""),
            "checkin_hour": metadata.get("checkinHour", ""),
            "checkout_hour": metadata.get("checkoutHour", ""),
            "extra_description": metadata.get("extraDescription", []),
            "lat": metadata.get("chalet", {}).get("lat", ""),
            "lng": metadata.get("chalet", {}).get("lng", "")
        }
        properties.append(details)

    # Generate QA response with RAG
    retriever_output = qa.run(input_documents=docs, question=query)
    return properties, retriever_output

# Example of querying the data
# query = "شقة قريبة من البوليفارد بسعر مناسب ريال غرفتين نوم مع تسجيل دخول ذاتي"
# as_output, retriever_output = query_data(query)

# print("Atlas Vector Search Output: ", as_output)
# print("RAG QA Output: ", retriever_output)