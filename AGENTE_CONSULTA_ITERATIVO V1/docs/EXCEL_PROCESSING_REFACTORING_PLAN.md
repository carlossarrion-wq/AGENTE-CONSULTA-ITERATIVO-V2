# Excel Processing Refactoring Plan

## Issues to Address

### 1. Duplicate Code in Excel Processing
There's code duplication between `_index_excel_document_optimized` and `_index_regular_document` in the indexing process.

### 2. Inconsistent Chunking Parameters
Chunking parameters are defined in multiple places and could get out of sync:
- `MultiAppOpenSearchIndexer` sets chunking parameters for `SemanticChunker`
- `OptimizedExcelLoader` has its own chunking logic with different parameters

## Proposed Solutions

### For Duplicate Code:
1. Extract common document metadata preparation into a shared method
2. Extract common chunk indexing logic into a shared method
3. Refactor both methods to use these shared methods

### For Inconsistent Chunking Parameters:
1. Create a centralized chunking configuration class
2. Update all components to use this centralized configuration
3. Ensure configuration is loaded from a single source

## Implementation Plan

### Step 1: Create Centralized Chunking Configuration
- Create a new class `ChunkingConfig` to hold all chunking parameters
- Load parameters from configuration files
- Provide defaults for all parameters

### Step 2: Extract Common Excel Processing Logic
- Create shared methods for document metadata preparation
- Create shared methods for chunk indexing

### Step 3: Update Components to Use Centralized Configuration
- Update `MultiAppOpenSearchIndexer`
- Update `SemanticChunker`
- Update `OptimizedExcelLoader`
- Update `OptimizedExcelIndexer`

### Step 4: Test Changes
- Ensure all tests pass with the refactored code
- Verify that Excel processing still works correctly
