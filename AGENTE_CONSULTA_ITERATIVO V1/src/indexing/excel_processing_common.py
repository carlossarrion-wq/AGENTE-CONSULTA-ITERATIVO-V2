"""
Excel Processing Common Functions
Provides shared functionality for Excel document processing and indexing
"""

from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime


def prepare_document_metadata(document: Dict[str, Any], app_name: str, 
                            app_info: Dict[str, Any], s3_config: Dict[str, Any],
                            chunking_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare common document metadata for indexing.
    
    Args:
        document: Document dictionary
        app_name: Application name
        app_info: Application information
        s3_config: S3 configuration
        chunking_config: Chunking configuration
        
    Returns:
        Dictionary with prepared metadata
    """
    return {
        **document.get('metadata', {}),
        'application_id': app_name,
        'application_name': app_info.get('name', app_name),
        'indexed_at': datetime.now().isoformat(),
        's3_bucket': s3_config.get('bucket', ''),
        's3_prefix': s3_config.get('documents_prefix', ''),
        'chunk_config': chunking_config,
        'file_size': document.get('file_size', 0),
        'file_extension': document.get('file_extension', '')
    }


def prepare_excel_chunk_metadata(base_metadata: Dict[str, Any], 
                               excel_chunk: Dict[str, Any],
                               chunk_index: int,
                               total_chunks: int) -> Dict[str, Any]:
    """
    Prepare metadata for an Excel chunk.
    
    Args:
        base_metadata: Base document metadata
        excel_chunk: Excel chunk data
        chunk_index: Index of the chunk
        total_chunks: Total number of chunks
        
    Returns:
        Dictionary with prepared chunk metadata
    """
    chunk_metadata = excel_chunk.get('metadata', {})
    
    return {
        **base_metadata,
        **chunk_metadata,
        "total_chunks": total_chunks,
        "chunk_processing_method": "optimized_excel_batch",
        "excel_sheet_name": excel_chunk.get('sheet_name', 'unknown'),
        "excel_sheet_index": excel_chunk.get('sheet_index', 0),
        "excel_row_start": excel_chunk.get('row_start', 0),
        "excel_row_end": excel_chunk.get('row_end', 0),
        "excel_row_count": excel_chunk.get('row_count', 0),
        "is_excel_optimized": True
    }


def prepare_chunk_for_indexing(chunk_content: str, document: Dict[str, Any],
                             chunk_id: str, chunk_index: int,
                             embedding: List[float], metadata: Dict[str, Any],
                             app_name: str, app_info: Dict[str, Any],
                             s3_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare a chunk for indexing in OpenSearch.
    
    Args:
        chunk_content: Content of the chunk
        document: Original document
        chunk_id: Unique ID for the chunk
        chunk_index: Index of the chunk
        embedding: Vector embedding for the chunk
        metadata: Chunk metadata
        app_name: Application name
        app_info: Application information
        s3_config: S3 configuration
        
    Returns:
        Dictionary ready for indexing
    """
    sheet_name = metadata.get('excel_sheet_name', 'Sheet')
    
    return {
        "content": chunk_content,
        "title": f"{document.get('file_name', '')} - {sheet_name}",
        "file_path": document.get('file_path', ''),
        "file_name": document.get('file_name', ''),
        "chunk_id": chunk_id,
        "chunk_index": chunk_index,
        "embedding": embedding,
        "metadata": metadata,
        "timestamp": datetime.now().isoformat(),
        "document_type": "excel_optimized",
        "has_images": False,
        "image_count": 0,
        # Application fields
        "application_id": app_name,
        "application_name": app_info.get('name', app_name),
        "s3_bucket": s3_config.get('bucket', ''),
        "s3_prefix": s3_config.get('documents_prefix', '')
    }


def log_excel_chunk_details(chunk_idx: int, excel_chunk: Dict[str, Any], 
                          metadata: Dict[str, Any], success: bool = True) -> None:
    """
    Log details about an Excel chunk.
    
    Args:
        chunk_idx: Index of the chunk
        excel_chunk: Excel chunk data
        metadata: Chunk metadata
        success: Whether indexing was successful
    """
    sheet_name = excel_chunk.get('sheet_name', 'unknown')
    row_start = excel_chunk.get('row_start', 0)
    row_end = excel_chunk.get('row_end', 0)
    row_count = excel_chunk.get('row_count', 0)
    codes_count = len(metadata.get('technical_codes', []))
    
    status = "Indexed" if success else "Failed to index"
    
    logger.debug(f"{status} Excel chunk {chunk_idx}: sheet '{sheet_name}', "
                f"rows {row_start+1}-{row_end} ({row_count} rows), {codes_count} codes")
