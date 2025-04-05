from typing import Dict, Any, List, Optional
import os
from pinecone import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
import requests
from bs4 import BeautifulSoup
from utils.config import get_openai_config, get_pinecone_config, get_app_config
from langchain.vectorstores import Pinecone as LangchainPinecone

class BotService:
    def __init__(self):
        self.openai_config = get_openai_config()
        self.pinecone_config = get_pinecone_config()
        self.app_config = get_app_config()
        
        # Set OpenAI API key in environment
        os.environ["OPENAI_API_KEY"] = self.openai_config["api_key"]
        
        # Initialize OpenAI embeddings using environment variable
        self.embeddings = OpenAIEmbeddings(disallowed_special=())
        
        # Initialize Pinecone with the new API
        self.pc = Pinecone(api_key=self.pinecone_config["api_key"])
        
        # Create a simple in-memory document store for immediate testing
        # This will be replaced with Pinecone once properly initialized
        self.init_document_store()
        
        # Initialize the LLM and chain
        self.llm = ChatOpenAI(
            model=self.openai_config["model"],
            temperature=self.openai_config["temperature"]
        )
        
        self.memory = ConversationBufferMemory(
            input_key="question",
            memory_key="chat_history"
        )
        
        self.qa_template = """You are Mark Musk, an AI assistant specialized in CreditChek API integration.
        Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        
        Chat History: {chat_history}
        
        Question: {question}
        
        Answer:"""
        
        self.qa_prompt = PromptTemplate(
            template=self.qa_template,
            input_variables=["context", "chat_history", "question"]
        )
        
        self.qa_chain = LLMChain(
            llm=self.llm,
            prompt=self.qa_prompt,
            memory=self.memory,
            output_key="answer",
            verbose=True
        )

    def init_document_store(self):
        """Initialize a document store with CreditChek API information."""
        # Create a more comprehensive in-memory store with API information
        self.sample_docs = [
            # Authentication
            Document(page_content="To authenticate with CreditChek API, you need to obtain an API key from the dashboard. Include it in the header of all requests as 'Authorization: Bearer YOUR_API_KEY'. All API requests must be made over HTTPS to ensure security. Example header: {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}"),
            
            # Identity Verification
            Document(page_content="CreditChek API provides identity verification through the /api/v1/identity endpoint. This endpoint requires parameters like first_name, last_name, dob, and id_number. The response includes verification status, confidence score, and person details if found."),
            Document(page_content="CreditChek identity verification example request: POST /api/v1/identity with body {'first_name': 'John', 'last_name': 'Doe', 'dob': '1990-01-01', 'id_number': 'A12345678X', 'id_type': 'NATIONAL_ID'}"),
            
            # BVN Verification
            Document(page_content="The CreditChek BVN Verification API allows you to verify a customer's identity using their Bank Verification Number (BVN). This is accessed via /api/v1/verify/bvn endpoint with the parameter 'bvn' containing the 11-digit BVN."),
            Document(page_content="CreditChek BVN verification example request: POST /api/v1/verify/bvn with body {'bvn': '12345678901'}"),
            
            # Credit Score
            Document(page_content="CreditChek's Credit Score API is available at /api/v1/credit-score and provides a comprehensive credit score based on various financial indicators. Required parameters include 'customer_id' to retrieve the score for a specific customer."),
            Document(page_content="CreditChek credit score example request: GET /api/v1/credit-score?customer_id=CID123456"),
            
            # Bank Statement Analysis
            Document(page_content="The Bank Statement Analysis API at /api/v1/statement-analysis provides insights into spending patterns, income verification, and financial behavior from bank statements. It accepts PDF or CSV statement files encoded in base64."),
            Document(page_content="CreditChek bank statement analysis example request: POST /api/v1/statement-analysis with body {'customer_id': 'CID123456', 'statement_file': 'base64_encoded_file', 'bank_code': 'GTB', 'statement_type': 'ACCOUNT'}"),
            
            # Error Handling
            Document(page_content="For error handling, CreditChek API returns standard HTTP status codes: 200 for success, 400 for bad requests, 401 for authentication errors, 404 for not found, and 500 for server errors. Each error response includes a 'message' field explaining the error."),
            
            # Rate Limiting
            Document(page_content="Rate limiting for CreditChek API is set at 100 requests per minute. If you exceed this limit, you'll receive a 429 Too Many Requests response with a 'Retry-After' header indicating when to retry."),
            
            # Base URL and Environments
            Document(page_content="The CreditChek API base URL is https://api.creditchek.africa/api/v1/ for production and https://sandbox.creditchek.africa/api/v1/ for sandbox testing."),
            
            # Headers
            Document(page_content="Required headers for CreditChek API requests include: 'Authorization: Bearer YOUR_API_KEY', 'Content-Type: application/json', and 'Accept: application/json'. For file uploads, use 'Content-Type: multipart/form-data'."),
            
            # Webhook Integration
            Document(page_content="CreditChek offers webhook integration for asynchronous notifications. Configure your webhook URL in the dashboard. Events include verification_complete, credit_score_updated, and statement_analyzed. All Webhook requests are sent with a x-auth-signature header for verification. It should match the secret key pair of the app public key you used when initiating the request."),
            
            # Webhook Events
            Document(page_content="Webhook events include: pdf_upload, borrower_onboarded, income_insight, income_transaction, credit_premium, credit_advanced"),
        ]
        
        # Map of API endpoints to sample code templates
        self.code_templates = {
            "authentication": {
                "Python": """import requests

def authenticate_request(api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    # Example API call
    response = requests.get(
        'https://api.creditchek.africa/api/v1/status',
        headers=headers
    )
    return response.json()

# Usage
api_key = 'YOUR_API_KEY'
result = authenticate_request(api_key)
print(result)""",
                
                "NodeJS": """const axios = require('axios');

async function authenticateRequest(apiKey) {
  const headers = {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
  
  try {
    const response = await axios.get(
      'https://api.creditchek.africa/api/v1/status',
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Authentication error:', error.response?.data || error.message);
    throw error;
  }
}

// Usage
const apiKey = 'YOUR_API_KEY';
authenticateRequest(apiKey)
  .then(result => console.log(result))
  .catch(err => console.error(err));""",
                
                "PHP Laravel": """<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class CreditChekService
{
    protected $apiKey;
    protected $baseUrl;
    
    public function __construct()
    {
        $this->apiKey = env('CREDITCHEK_API_KEY');
        $this->baseUrl = 'https://api.creditchek.africa/api/v1';
    }
    
    protected function getHeaders()
    {
        return [
            'Authorization' => 'Bearer ' . $this->apiKey,
            'Content-Type' => 'application/json',
            'Accept' => 'application/json',
        ];
    }
    
    public function checkApiStatus()
    {
        try {
            $response = Http::withHeaders($this->getHeaders())
                          ->get($this->baseUrl . '/status');
            
            return $response->json();
        } catch (\Exception $e) {
            report($e);
            return ['error' => $e->getMessage()];
        }
    }
}""",
                
                "GoLang": """package creditchek

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

type CreditChekClient struct {
	ApiKey  string
	BaseURL string
}

func NewCreditChekClient(apiKey string) *CreditChekClient {
	return &CreditChekClient{
		ApiKey:  apiKey,
		BaseURL: "https://api.creditchek.africa/api/v1",
	}
}

func (c *CreditChekClient) CheckAPIStatus() (map[string]interface{}, error) {
	req, err := http.NewRequest("GET", c.BaseURL+"/status", nil)
	if err != nil {
		return nil, err
	}
	
	req.Header.Add("Authorization", "Bearer "+c.ApiKey)
	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Accept", "application/json")
	
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	
	var result map[string]interface{}
	err = json.Unmarshal(body, &result)
	return result, err
}

func main() {
	client := NewCreditChekClient("YOUR_API_KEY")
	result, err := client.CheckAPIStatus()
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	fmt.Println(result)
}"""
            },
            
            "identity_verification": {
                "Python": """import requests

def verify_identity(api_key, first_name, last_name, dob, id_number, id_type="NATIONAL_ID"):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'first_name': first_name,
        'last_name': last_name,
        'dob': dob,  # Format: YYYY-MM-DD
        'id_number': id_number,
        'id_type': id_type
    }
    
    try:
        response = requests.post(
            'https://api.creditchek.africa/api/v1/identity',
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error verifying identity: {e}")
        return None

# Usage
api_key = 'YOUR_API_KEY'
result = verify_identity(
    api_key,
    first_name="John",
    last_name="Doe",
    dob="1990-01-01",
    id_number="A12345678X"
)
print(result)""",

                "NodeJS": """const axios = require('axios');

async function verifyIdentity(apiKey, firstName, lastName, dob, idNumber, idType = 'NATIONAL_ID') {
  const headers = {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  };
  
  const payload = {
    first_name: firstName,
    last_name: lastName,
    dob: dob, // Format: YYYY-MM-DD
    id_number: idNumber,
    id_type: idType
  };
  
  try {
    const response = await axios.post(
      'https://api.creditchek.africa/api/v1/identity',
      payload,
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Identity verification error:', error.response?.data || error.message);
    throw error;
  }
}

// Usage
const apiKey = 'YOUR_API_KEY';
verifyIdentity(
  apiKey,
  'John',
  'Doe',
  '1990-01-01',
  'A12345678X'
)
  .then(result => console.log(result))
  .catch(err => console.error(err));""",
            }
            # Other code templates can be added similarly
        }
        
        # TODO: Once Pinecone is properly working, this will be replaced with vector search

    def generate_code_snippets(self, endpoint_info: str) -> Dict[str, str]:
        """Generate code snippets for different programming languages."""
        prompt = f"""
        Generate code snippets for the following CreditChek API endpoint:
        {endpoint_info}
        
        Please provide examples in these languages: {', '.join(self.app_config['supported_languages'])}
        Include proper error handling and best practices.
        """
        
        response = self.llm.predict(prompt)
        
        # Parse the response and extract code snippets
        snippets = {}
        for lang in self.app_config["supported_languages"]:
            if lang.lower() in response.lower():
                # Extract code block for the language
                start = response.lower().find(lang.lower())
                end = response.find("```", start + len(lang))
                if end != -1:
                    code_end = response.find("```", end + 3)
                    if code_end != -1:
                        snippets[lang] = response[end + 3:code_end].strip()
        
        return snippets

    def generate_response(self, query: str) -> Dict[str, Any]:
        """Generate a response to the user's query."""
        # First, handle some common specific queries directly
        query_lower = query.lower()
        
        # Check for "Show X Example" patterns
        show_example_match = None
        for lang in self.app_config["supported_languages"]:
            if f"show {lang.lower()} example" in query_lower:
                show_example_match = lang
                break
        
        if show_example_match:
            # Find the most appropriate example
            if "authentication" in self.code_templates and show_example_match in self.code_templates["authentication"]:
                return {
                    "text": f"Here's a {show_example_match} example for authenticating with the CreditChek API:",
                    "code_snippets": {
                        show_example_match: self.code_templates["authentication"][show_example_match]
                    }
                }
            elif "identity_verification" in self.code_templates and show_example_match in self.code_templates["identity_verification"]:
                return {
                    "text": f"Here's a {show_example_match} example for identity verification with the CreditChek API:",
                    "code_snippets": {
                        show_example_match: self.code_templates["identity_verification"][show_example_match]
                    }
                }
            else:
                # Generate a generic example
                code_snippets = self.generate_code_snippets(f"CreditChek API basic {show_example_match} integration example")
                if show_example_match in code_snippets:
                    return {
                        "text": f"Here's a {show_example_match} example for integrating with the CreditChek API:",
                        "code_snippets": {
                            show_example_match: code_snippets[show_example_match]
                        }
                    }
        
        # Handle library questions
        if "library" in query_lower or "libraries" in query_lower or "package" in query_lower or "packages" in query_lower:
            return {
                "text": "Yes, there are several libraries that can simplify CreditChek API integration:\n\n" +
                       "For Python:\n" +
                       "- Requests: The standard for HTTP requests in Python\n" +
                       "- CreditChek-Python-SDK: Official Python SDK for CreditChek (if available)\n\n" +
                       "For NodeJS:\n" +
                       "- Axios: Promise-based HTTP client\n" +
                       "- Node-Fetch: Lightweight fetch API implementation\n\n" +
                       "For PHP Laravel:\n" +
                       "- Guzzle HTTP: PHP HTTP client\n" +
                       "- Laravel HTTP Client: Built-in HTTP client for Laravel\n\n" +
                       "For GoLang:\n" +
                       "- Net/HTTP: Standard library for HTTP requests\n" +
                       "- Go-Resty: Simple HTTP and REST client library\n\n" +
                       "These libraries handle HTTP requests, authentication, and response parsing, making API integration faster and more reliable."
            }
        
        # Handle header-related queries directly
        if "header" in query_lower or "authentication" in query_lower or "auth" in query_lower:
            return {
                "text": "For CreditChek API requests, you need to include the following headers:\n\n" + 
                        "- 'Authorization: Bearer YOUR_API_KEY' - Required for authentication\n" + 
                        "- 'Content-Type: application/json' - For JSON request bodies\n" +
                        "- 'Accept: application/json' - To receive JSON responses\n\n" +
                        "For file upload endpoints, use 'Content-Type: multipart/form-data' instead."
            }
        
        # Regular query handling with document retrieval
        relevant_docs = []
        for doc in self.sample_docs:
            # Better relevance check using multiple keywords
            keywords = query_lower.split()
            if any(keyword in doc.page_content.lower() for keyword in keywords):
                relevant_docs.append(doc)
        
        # If no matching docs found, use a few random ones to provide some context
        if not relevant_docs:
            import random
            relevant_docs = random.sample(self.sample_docs, min(3, len(self.sample_docs)))
            
        context = "\n".join([doc.page_content for doc in relevant_docs])
        
        # Get response from QA chain
        chain_response = self.qa_chain({
            "context": context,
            "question": query
        })
        
        response = chain_response["answer"]
        
        # Check if the query is about an API endpoint
        if any(keyword in query_lower for keyword in ["api", "endpoint", "integration", "code", "example"]):
            # Generate code snippets
            code_snippets = self.generate_code_snippets(response)
            
            return {
                "text": response,
                "code_snippets": code_snippets
            }
        
        return {"text": response}
