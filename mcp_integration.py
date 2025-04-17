import json
import os
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

class CompanyDataMCPServer:
    """MCP Server implementation for accessing company data"""
    
    def __init__(self, data_path):
        """Initialize the MCP server with company data"""
        self.data_path = data_path
        self.load_data()
        
    def load_data(self):
        """Load company data from JSON file and compute embeddings."""
        try:
            with open(self.data_path, 'r') as f:
                self.company_data = json.load(f)
            print(f"Loaded {len(self.company_data)} company data documents")
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            # Compute embeddings for each document (title + content)
            self.doc_texts = [doc['title'] + ' ' + doc['content'] for doc in self.company_data]
            self.doc_embeddings = self.embedding_model.encode(self.doc_texts, convert_to_numpy=True)
        except Exception as e:
            print(f"Error loading company data or computing embeddings: {e}")
            self.company_data = []
            self.doc_embeddings = None
            self.embedding_model = None
    
    def search_data(self, query, top_k=3, similarity_threshold=0.3):
        """Search company data using embedding similarity. Always return top_k most similar documents regardless of score. Logs debug info."""
        print("\n[MCP DEBUG] --- search_data called ---")
        print(f"[MCP DEBUG] Query: {query}")
        if not hasattr(self, 'embedding_model') or self.embedding_model is None or self.doc_embeddings is None:
            print("[MCP DEBUG] Embedding model not initialized. Using keyword search fallback.")
            query_l = query.lower()
            results = [doc for doc in self.company_data if query_l in doc['title'].lower() or query_l in doc['content'].lower()]
            print(f"[MCP DEBUG] Keyword search results: {len(results)}")
            for doc in results:
                print(f"[MCP DEBUG]  - {doc['title']}")
            print(f"[DEBUG] Returning from keyword search: {results}")
            return results
        print(f"[MCP DEBUG] Using embedding-based search. Doc count: {len(self.company_data)}")
        print("[MCP DEBUG] Document titles:")
        for i, doc in enumerate(self.company_data):
            print(f"  [{i}] {doc['title']}")
        query_emb = self.embedding_model.encode([query], convert_to_numpy=True)[0]
        similarities = np.dot(self.doc_embeddings, query_emb) / (np.linalg.norm(self.doc_embeddings, axis=1) * np.linalg.norm(query_emb) + 1e-10)
        print("[MCP DEBUG] Similarity scores:")
        for i, score in enumerate(similarities):
            print(f"  [{i}] {self.company_data[i]['title']}: {score:.3f}")
        top_indices = np.argsort(similarities)[::-1]
        results = [self.company_data[idx] for idx in top_indices[:top_k]]
        print(f"[MCP DEBUG] Final results: {len(results)}")
        for doc in results:
            print(f"[MCP DEBUG]  - {doc['title']}")
        print(f"[DEBUG] Returning from embedding search: {results}")
        print("[MCP DEBUG] --- end search_data ---\n")
        return results

    async def handle_request(self, request):
        """Handle MCP request and return relevant company data"""
        query = request.get('query', '')
        results = self.search_data(query)
        
        # Format results for MCP response
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result['title'],
                "content": result['content'],
                "source": f"Company Database - {result['id']}"
            })
            
        return {
            "results": formatted_results,
            "query": query,
            "total_results": len(formatted_results)
        }

class CompanyDataMCPClient:
    """MCP Client implementation for requesting company data"""
    
    def __init__(self, server):
        """Initialize the MCP client with a reference to the server"""
        self.server = server
        
    async def request_company_data(self, query):
        """Request company data from the MCP server"""
        request = {
            "query": query,
            "type": "company_data"
        }
        
        # In a real implementation, this would be a network request
        # For demo purposes, we directly call the server's handle_request method
        response = await self.server.handle_request(request)
        print(f"[DEBUG] MCP Client received response: {response}")
        print(f"[DEBUG] Before formatting: {response}")
        return response
    
    def format_for_llm(self, response):
        """Format MCP response for inclusion in LLM context"""
        print(f"[DEBUG] Formatting for LLM, input response: {response}")
        if not response or not response.get('results'):
            print("[DEBUG] No results found in MCP response.")
            return "No relevant company information found."
        
        formatted_text = "COMPANY INFORMATION:\n\n"
        
        for result in response['results']:
            formatted_text += f"--- {result['title']} ---\n"
            formatted_text += f"{result['content']}\n\n"
        print(f"[DEBUG] Formatted LLM context: {formatted_text}")
        return formatted_text

# Helper function to create MCP client and server instances
def setup_mcp(data_path):
    """Set up MCP client and server for company data"""
    server = CompanyDataMCPServer(data_path)
    client = CompanyDataMCPClient(server)
    return client, server

# --- TEST CODE ---
def _test_embedding_search():
    """Test embedding-based search for founding date."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "company_data.json")
    server = CompanyDataMCPServer(data_path)
    results = server.search_data("When was TechCorp founded?")
    print("[TEST] Results for 'When was TechCorp founded?':")
    for r in results:
        print(f"  - {r['title']}: {r['content']}")
    assert any("2010" in r['content'] for r in results), "Founding year not found in results!"
    print("[TEST] Passed: Founding date present in results.")
