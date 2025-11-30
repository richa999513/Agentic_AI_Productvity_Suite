"""Vector store for semantic search and memory retrieval."""
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from config.settings import settings
from config.logging_config import logger
import os


class VectorStore:
    """Manages vector embeddings for semantic search."""
    
    def __init__(self):
        # Create persist directory
        os.makedirs(settings.chroma_persist_directory, exist_ok=True)
        
        # Initialize Chroma client
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.chroma_persist_directory,
            anonymized_telemetry=False
        ))
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        
        # Collections
        self.notes_collection = self._get_or_create_collection("notes")
        self.tasks_collection = self._get_or_create_collection("tasks")
        self.memory_collection = self._get_or_create_collection("memories")
    
    def _get_or_create_collection(self, name: str):
        """Get or create a collection."""
        try:
            return self.client.get_or_create_collection(name=name)
        except Exception as e:
            logger.error(f"Error creating collection {name}: {e}")
            raise
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        return self.embedding_model.encode(text).tolist()
    
    def add_note(self, note_id: str, user_id: str, title: str, content: str, 
                 metadata: Optional[Dict[str, Any]] = None):
        """Add note to vector store."""
        try:
            text = f"{title}\n{content}"
            embedding = self._generate_embedding(text)
            
            meta = metadata or {}
            meta.update({"user_id": user_id, "type": "note"})
            
            self.notes_collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[meta],
                ids=[note_id]
            )
            logger.debug(f"Added note to vector store: {note_id}")
        except Exception as e:
            logger.error(f"Error adding note to vector store: {e}")
    
    def add_task(self, task_id: str, user_id: str, title: str, description: str,
                 metadata: Optional[Dict[str, Any]] = None):
        """Add task to vector store."""
        try:
            text = f"{title}\n{description or ''}"
            embedding = self._generate_embedding(text)
            
            meta = metadata or {}
            meta.update({"user_id": user_id, "type": "task"})
            
            self.tasks_collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[meta],
                ids=[task_id]
            )
            logger.debug(f"Added task to vector store: {task_id}")
        except Exception as e:
            logger.error(f"Error adding task to vector store: {e}")
    
    def add_memory(self, memory_id: str, user_id: str, content: str,
                   metadata: Optional[Dict[str, Any]] = None):
        """Add memory to vector store."""
        try:
            embedding = self._generate_embedding(content)
            
            meta = metadata or {}
            meta.update({"user_id": user_id, "type": "memory"})
            
            self.memory_collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[meta],
                ids=[memory_id]
            )
            logger.debug(f"Added memory to vector store: {memory_id}")
        except Exception as e:
            logger.error(f"Error adding memory to vector store: {e}")
    
    def search_notes(self, query: str, user_id: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search notes by semantic similarity."""
        try:
            query_embedding = self._generate_embedding(query)
            
            results = self.notes_collection.query(
                query_embeddings=[query_embedding],
                where={"user_id": user_id},
                n_results=n_results
            )
            
            return self._format_results(results)
        except Exception as e:
            logger.error(f"Error searching notes: {e}")
            return []
    
    def search_tasks(self, query: str, user_id: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search tasks by semantic similarity."""
        try:
            query_embedding = self._generate_embedding(query)
            
            results = self.tasks_collection.query(
                query_embeddings=[query_embedding],
                where={"user_id": user_id},
                n_results=n_results
            )
            
            return self._format_results(results)
        except Exception as e:
            logger.error(f"Error searching tasks: {e}")
            return []
    
    def search_memories(self, query: str, user_id: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search memories by semantic similarity."""
        try:
            query_embedding = self._generate_embedding(query)
            
            results = self.memory_collection.query(
                query_embeddings=[query_embedding],
                where={"user_id": user_id},
                n_results=n_results
            )
            
            return self._format_results(results)
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    def _format_results(self, results: Dict) -> List[Dict[str, Any]]:
        """Format Chroma results."""
        formatted = []
        
        if not results or not results.get('ids'):
            return formatted
        
        for i, doc_id in enumerate(results['ids'][0]):
            formatted.append({
                'id': doc_id,
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted
    
    def delete_note(self, note_id: str):
        """Delete note from vector store."""
        try:
            self.notes_collection.delete(ids=[note_id])
        except Exception as e:
            logger.error(f"Error deleting note: {e}")
    
    def delete_task(self, task_id: str):
        """Delete task from vector store."""
        try:
            self.tasks_collection.delete(ids=[task_id])
        except Exception as e:
            logger.error(f"Error deleting task: {e}")


# Global vector store instance
vector_store = VectorStore()