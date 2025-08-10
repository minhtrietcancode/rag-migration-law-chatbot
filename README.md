# Migration Act Chatbot

## Table of Contents

*   [Demo](#demo)
*   [Ideas and Approach](#ideas-and-approach)
*   [Workflow and Structure](#workflow-and-structure)
    *   [Repository Hierarchy](#repository-hierarchy)
    *   [1. Data Preparation (`data_preparation/`)](#1-data-preparation-data_preparation)
    *   [2. Chatbot Application (`src/`)](#2-chatbot-application-src)
*   [Installation](#installation)
*   [How to Run](#how-to-run)
*   [Limitation and Contributing](#limitation-and-contributing)
*   [License](#license)

## Demo

Here's a glimpse of the Migration Act Chatbot in action:

**Light Mode Default UI:**
![Light Mode Default UI](demo/Migration%20Act%20FE%20Light%20Mode%20Default.png)

**Dark Mode Default UI:**
![Dark Mode Default UI](demo/Migration%20Act%20FE%20Dark%20Mode%20Default.png)

**Search Tree Visualization:**
![Search Tree Visualization](demo/Migration%20Act%20Search%20Tree%20Visualization.png)

(A video demonstration is available at [Migration Act Assistant Demo](https://drive.google.com/file/d/1ZhROV9B09qwlQ5uMPdAlr5F1PSXkPMIw/view?usp=sharing))

An intelligent chatbot specializing in the Australian Migration Act 1958, designed to provide accurate and relevant information from the Act based on user queries. This project demonstrates a Retrieval-Augmented Generation (RAG) approach, combining a custom-built hierarchical search tree with vector embeddings and a Language Model (LLM) for efficient information retrieval and conversational response generation.

## Ideas and Approach

The core idea behind this chatbot is to overcome the limitations of traditional LLMs in accessing specific, up-to-date, and authoritative legal documents. By pre-processing the Migration Act 1958 and structuring its content into a searchable format, the chatbot can "retrieve" relevant sections before "generating" a response, ensuring accuracy and factual grounding.

Instead of embedding the entirety of the Migration Act, which would be prohibitively resource-intensive, this project simulates a human-like agentic searching approach. The system navigates a hierarchical tree structure, intelligently choosing the most relevant branch to explore at each step (e.g., going through a specific part, then a division, and so on). This significantly decreases the time complexity for searching, achieving logarithmic time complexity, O(log N), or even better, as each node in the tree can have multiple children. This approach is particularly intelligent for scalability; if the project were to expand to include hundreds of related legal documents, a brute-force embedding and search strategy would be extremely slow and resource-consuming. The current tree structure is designed to be extensible, potentially serving as a directory within a much larger, more comprehensive knowledge tree in future expansions.

## Workflow and Structure

The project workflow is systematically divided into two main phases: `data_preparation/` and `src/`.

### Repository Hierarchy

```
rag-migration-law-chatbot/
├── data_preparation/
│   ├── building_search_tree/
│   ├── building_tree_index/
│   ├── embedding_optimized_tree/
│   ├── extract_content_pages/
│   └── extract_index_pages/
├── demo/ # Contains the demo images and video
├── extracted_index_pages/ 
├── final_json_searching_material/ 
├── frontend/ 
│   ├── static/
│   └── templates/
├── json_search_tree/ 
├── json_tree_index/ 
├── Migration Act 1958/ # Contains the Migration Act PDF files
├── Migration Act Content Pages Txt Format/
├── src/
│   ├── database_admin_package/
│   ├── my_metadata_loader_package/
│   ├── my_searcher_package/
│   ├── search_term_handler_package/
│   ├── app.py
│   ├── config.py
│   └── main.py
├── vector_database/
├── .gitignore
├── README.md
└── requirements.txt
```

### 1. Data Preparation (`data_preparation/`)

This phase focuses on processing the raw Migration Act PDF files, extracting and structuring their content, and creating vector embeddings. This pre-processing ensures that the chatbot has a well-organized and semantically searchable knowledge base. The steps are executed in a specific order:

-   **`extract_index_pages`**:
    This initial step involves parsing the Migration Act PDF files to identify and extract their internal index structures. These indexes are crucial as they form the foundational hierarchical representation of the Act, akin to a table of contents. The extracted index information is saved within the `extracted_index_pages` folder.

-   **`building_tree_index`**:
    Following the extraction of index pages, this step constructs a preliminary, hierarchical tree-like index from the extracted data. This tree structure mirrors the logical organization of the Migration Act, with parts, divisions, and sections. The generated tree index is stored as JSON files in the `json_tree_index` folder.

-   **`building_search_tree`**:
    Based on the refined tree index, a more optimized search tree is built. This optimization focuses on creating a structure that facilitates efficient traversal and search operations during the chatbot's runtime. The various iterations and the final version of this search tree are saved in the `json_search_tree` folder.

-   **`extract_content_pages`**:
    Concurrently with building the tree structures, this step extracts the full textual content from each page of the Migration Act PDF files. The extracted text is then cleaned and saved as individual `.txt` files in the `Migration Act Content Pages Txt Format` folder. This ensures that the raw content for any selected section is readily available for O(1) lookup.

-   **`embedding_optimized_tree`**:
    This is a pivotal step for enabling semantic search. Each node within the optimized search tree (from `json_search_tree`) is transformed into a numerical vector embedding. These embeddings are then stored in a dedicated vector database (`vector_database/`), specifically ChromaDB. To ensure unique identification and direct retrieval, each node's name in the search tree is integrated with a unique ID (e.g., "Section name_code_vol_id"). A critical `final_hashmap.json` is also generated and placed in `final_json_searching_material/`, which provides an O(1) lookup mechanism for comprehensive section metadata (like starting and ending page numbers) once a relevant node is identified via vector search.

### 2. Chatbot Application (`src/`)

This phase houses the live chatbot functionality, processing user queries, performing intelligent searches, and generating conversational responses.

-   **`search_term_handler_package`**:
    This package is the first point of contact for a user's question. It utilizes a Language Model (LLM) to analyze the natural language input and distil it into a concise, focused search term. This search term is then converted into a high-dimensional vector representation using a Sentence Transformer model, making it suitable for semantic similarity comparisons.

-   **`my_searcher_package`**:
    Receiving the embedded search term, the `MySearcher` component initiates a search on the pre-built, optimized search tree. It employs a greedy Depth-First Search (DFS) algorithm, navigating the tree by calculating the cosine similarity between the user's embedded search term and the pre-embedded vectors of the tree nodes. This greedy approach prioritizes paths that are most semantically relevant to the query.

-   **`database_admin_package`**:
    This package serves as the interface to the ChromaDB vector store (`vector_database/`). Throughout the search process in `my_searcher`, the `database_admin` is called upon to retrieve the pre-embedded vectors of specific tree nodes. This allows for real-time cosine similarity calculations, guiding the greedy DFS towards the most pertinent sections of the Migration Act.

-   **`main.py`**:
    As the central orchestrator, `main.py` integrates all the backend components. It manages the main chat loop, deciding whether a user's question requires a database search or a general conversational response. It calls upon the `search_term_handler`, `my_searcher`, and `database_admin` as needed, and finally leverages an LLM (LangChain) to generate a coherent and informative response to the user.

-   **`app.py` and `frontend/`**:
    The user interface of the chatbot is powered by a Flask web application configured in `app.py`. This `app.py` serves as the backend API, receiving user messages and sending back chatbot responses. The `frontend/` directory contains all the client-side assets: `index.html` (the main web page), `styles.css` (for visual styling, including a dark/light mode toggle), and `script.js` (handling user interactions, sending messages to the backend, and displaying responses dynamically). The Flask application connects these static frontend assets to the Python backend, providing a seamless conversational experience.

## Installation

To set up and run the Migration Act Chatbot locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/minhtrietcancode/rag-migration-law-chatbot
    cd rag-migration-law-chatbot
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    -   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    -   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Prepare environment variables:**
    Create a `.env` file in the root directory of the project with your API keys:
    ```
    OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY"
    ```
    (You'll need to obtain an API key from [OpenRouter.ai](https://openrouter.ai/).)

## How to Run

To run the chatbot application, ensure you have completed the [Installation](#installation) steps and then follow these additional steps:

1.  **Prepare the Vector Database:**
    Before running the chatbot, you need to ensure the vector database is initialized and populated with embeddings.
    ```bash
    mkdir vector_database
    python data_preparation/embedding_optimized_tree/embed_save_chromadb.py
    ```

2.  **Start the Chatbot Application:**
    Navigate to the root directory of the project and run the Flask application:

    ```bash
    python src/app.py
    ```

    The application will typically run on `http://127.0.0.1:5000/`. Open this URL in your web browser to interact with the Migration Act Chatbot.

## Limitation and Contributing

The current search approach utilizes a greedy algorithm during tree traversal. While highly efficient (approaching O(log N) time complexity), this greedy nature introduces a trade-off with the correctness of the search results, as it may sometimes "skip" a potentially relevant node if its immediate similarity score isn't the highest. This limitation can be optimized in future iterations by exploring more sophisticated algorithms, such as introducing backpropagation or backtracking steps based on similarity thresholds or confidence scores during traversal.

Contributions to improve the search algorithm, expand the knowledge base, or enhance the user interface are highly welcome. Feel free to open issues or submit pull requests!

## License

This project is licensed under the [MIT License](LICENSE).