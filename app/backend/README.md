# Backend for RAG Chat App with Azure OpenAI and Azure AI Search

This directory contains the backend code for the RAG Chat App, which uses Azure OpenAI Service and Azure AI Search to provide a ChatGPT-like experience over your own documents.

## Overview

The backend is responsible for:
- Handling API requests from the frontend.
- Interacting with Azure OpenAI Service to generate responses.
- Using Azure AI Search to index and retrieve documents.

## Setup Instructions

### Prerequisites

- Python 3.9, 3.10, or 3.11
- Azure account with necessary permissions
- Azure Developer CLI

### Installation

1. Clone the repository:
    ```shell
    git clone https://github.com/azure-samples/azure-search-openai-demo.git
    cd azure-search-openai-demo/app/backend
    ```

2. Create a virtual environment and activate it:
    ```shell
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```shell
    pip install -r requirements.txt
    ```

## Usage

1. Run the development server:
    ```shell
    python main.py
    ```

2. The server will start on `http://127.0.0.1:8000`. You can interact with the API using this URL.

## Configuration

Configuration settings for the backend can be found in the `config.py` file. Ensure you update the necessary settings such as Azure credentials and endpoints.

## Deployment

To deploy the backend to Azure, follow the instructions in the main README.md file.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.