Introduction
Official Website Discord Follow

GitHub Repo stars Twitter Follow PyPI version Open In Colab

GPT Researcher is an autonomous agent designed for comprehensive online research on a variety of tasks.

The agent can produce detailed, factual and unbiased research reports, with customization options for focusing on relevant resources, outlines, and lessons. Inspired by the recent Plan-and-Solve and RAG papers, GPT Researcher addresses issues of speed, determinism and reliability, offering a more stable performance and increased speed through parallelized agent work, as opposed to synchronous operations.

Why GPT Researcher?
To form objective conclusions for manual research tasks can take time, sometimes weeks to find the right resources and information.
Current LLMs are trained on past and outdated information, with heavy risks of hallucinations, making them almost irrelevant for research tasks.
Current LLMs are limited to short token outputs which are not sufficient for long detailed research reports (2k+ words).
Solutions that enable web search (such as ChatGPT + Web Plugin), only consider limited resources and content that in some cases result in superficial conclusions or biased answers.
Using only a selection of resources can create bias in determining the right conclusions for research questions or tasks.
Architecture
The main idea is to run "planner" and "execution" agents, whereas the planner generates questions to research, and the execution agents seek the most related information based on each generated research question. Finally, the planner filters and aggregates all related information and creates a research report.

The agents leverage both gpt-4o-mini and gpt-4o (128K context) to complete a research task. We optimize for costs using each only when necessary. The average research task takes around 3 minutes to complete, and costs ~$0.1.


More specifically:

Create a domain specific agent based on research query or task.
Generate a set of research questions that together form an objective opinion on any given task.
For each research question, trigger a crawler agent that scrapes online resources for information relevant to the given task.
For each scraped resources, summarize based on relevant information and keep track of its sources.
Finally, filter and aggregate all summarized sources and generate a final research report.
Demo

Tutorials
Video Tutorial Series
How it Works
How to Install
Live Demo
Homepage
Features
📝 Generate research, outlines, resources and lessons reports
📜 Can generate long and detailed research reports (over 2K words)
🌐 Aggregates over 20 web sources per research to form objective and factual conclusions
🖥️ Includes an easy-to-use web interface (HTML/CSS/JS)
🔍 Scrapes web sources with javascript support
📂 Keeps track and context of visited and used web sources
📄 Export research reports to PDF, Word and more...
Let's get started here!




PIP Package
PyPI version Open In Colab

🌟 Exciting News! Now, you can integrate gpt-researcher with your apps seamlessly!

Steps to Install GPT Researcher
Follow these easy steps to get started:

Pre-requisite: Ensure Python 3.10+ is installed on your machine 💻
Install gpt-researcher: Grab the official package from PyPi.
pip install gpt-researcher

Environment Variables: Create a .env file with your OpenAI API key or simply export it
export OPENAI_API_KEY={Your OpenAI API Key here}

export TAVILY_API_KEY={Your Tavily API Key here}

Start using GPT Researcher in your own codebase
Example Usage
from gpt_researcher import GPTResearcher
import asyncio

async def get_report(query: str, report_type: str):
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    
    # Get additional information
    research_context = researcher.get_research_context()
    research_costs = researcher.get_costs()
    research_images = researcher.get_research_images()
    research_sources = researcher.get_research_sources()
    
    return report, research_context, research_costs, research_images, research_sources

if __name__ == "__main__":
    query = "what team may win the NBA finals?"
    report_type = "research_report"

    report, context, costs, images, sources = asyncio.run(get_report(query, report_type))
    
    print("Report:")
    print(report)
    print("\nResearch Costs:")
    print(costs)
    print("\nNumber of Research Images:")
    print(len(images))
    print("\nNumber of Research Sources:")
    print(len(sources))

Specific Examples
Example 1: Research Report
query = "Latest developments in renewable energy technologies"
report_type = "research_report"

Example 2: Resource Report
query = "List of top AI conferences in 2023"
report_type = "resource_report"

Example 3: Outline Report
query = "Outline for an article on the impact of AI in education"
report_type = "outline_report"

Integration with Web Frameworks
FastAPI Example
from fastapi import FastAPI
from gpt_researcher import GPTResearcher
import asyncio

app = FastAPI()

@app.get("/report/{report_type}")
async def get_report(query: str, report_type: str) -> dict:
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    
    source_urls = researcher.get_source_urls()
    research_costs = researcher.get_costs()
    research_images = researcher.get_research_images()
    research_sources = researcher.get_research_sources()
    
    return {
        "report": report,
        "source_urls": source_urls,
        "research_costs": research_costs,
        "num_images": len(research_images),
        "num_sources": len(research_sources)
    }

# Run the server
# uvicorn main:app --reload

Flask Example
Pre-requisite: Install flask with the async extra.

pip install 'flask[async]'

from flask import Flask, request, jsonify
from gpt_researcher import GPTResearcher

app = Flask(__name__)

@app.route('/report/<report_type>', methods=['GET'])
async def get_report(report_type):
    query = request.args.get('query')
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    
    source_urls = researcher.get_source_urls()
    research_costs = researcher.get_costs()
    research_images = researcher.get_research_images()
    research_sources = researcher.get_research_sources()
    
    return jsonify({
        "report": report,
        "source_urls": source_urls,
        "research_costs": research_costs,
        "num_images": len(research_images),
        "num_sources": len(research_sources)
    })

# Run the server
# flask run

Run the server

flask run

Example Request

curl -X GET "http://localhost:5000/report/research_report?query=what team may win the nba finals?"

Getters and Setters
GPT Researcher provides several methods to retrieve additional information about the research process:

Get Research Sources
Sources are the URLs that were used to gather information for the research.

source_urls = researcher.get_source_urls()

Get Research Context
Context is all the retrieved information from the research. It includes the sources and their corresponding content.

research_context = researcher.get_research_context()

Get Research Costs
Costs are the number of tokens consumed during the research process.

research_costs = researcher.get_costs()

Get Research Images
Retrieves a list of images found during the research process.

research_images = researcher.get_research_images()

Get Research Sources
Retrieves a list of research sources, including title, content, and images.

research_sources = researcher.get_research_sources()

Set Verbose
You can set the verbose mode to get more detailed logs.

researcher.set_verbose(True)

Add Costs
You can also add costs to the research process if you want to track the costs from external usage.

researcher.add_costs(0.22)

Advanced Usage
Customizing the Research Process
You can customize various aspects of the research process by passing additional parameters when initializing the GPTResearcher:

researcher = GPTResearcher(
    query="Your research query",
    report_type="research_report",
    report_format="APA",
    tone="formal and objective",
    max_subtopics=5,
    verbose=True
)

Handling Research Results
After conducting research, you can process the results in various ways:

# Conduct research
research_result = await researcher.conduct_research()

# Generate a standard report
report = await researcher.write_report()

# Generate a customized report with specific formatting requirements
custom_report = await researcher.write_report(custom_prompt="Answer in short, 2 paragraphs max without citations.")

# Generate a focused report for a specific audience
executive_summary = await researcher.write_report(custom_prompt="Create an executive summary focused on business impact and ROI. Keep it under 500 words.")

# Generate a report with specific structure requirements
technical_report = await researcher.write_report(custom_prompt="Create a technical report with problem statement, methodology, findings, and recommendations sections.")

# Generate a conclusion
conclusion = await researcher.write_report_conclusion(report)

# Get subtopics
subtopics = await researcher.get_subtopics()

# Get draft section titles for a subtopic
draft_titles = await researcher.get_draft_section_titles("Subtopic name")


Customizing Report Generation with Custom Prompts
The write_report method accepts a custom_prompt parameter that gives you complete control over how your research is presented:

# After conducting research
research_result = await researcher.conduct_research()

# Generate a report with a custom prompt
report = await researcher.write_report(
    custom_prompt="Based on the research, provide a bullet-point summary of the key findings."
)

Custom prompts can be used for various purposes:

Format Control: Specify the structure, length, or style of your report

report = await researcher.write_report(
    custom_prompt="Write a blog post in a conversational tone using the research. Include headings and a conclusion."
)


Audience Targeting: Tailor the content for specific readers

report = await researcher.write_report(
    custom_prompt="Create a report for technical stakeholders, focusing on methodologies and implementation details."
)


Specialized Outputs: Generate specific types of content

report = await researcher.write_report(
    custom_prompt="Create a FAQ section based on the research with at least 5 questions and detailed answers."
)


The custom prompt will be combined with the research context to generate your customized report.

Working with Research Context
You can use the research context for further processing or analysis:

# Get the full research context
context = researcher.get_research_context()

# Get similar written contents based on draft section titles
similar_contents = await researcher.get_similar_written_contents_by_draft_section_titles(
    current_subtopic="Subtopic name",
    draft_section_titles=["Title 1", "Title 2"],
    written_contents=some_written_contents,
    max_results=10
)

This comprehensive documentation should help users understand and utilize the full capabilities of the GPT Researcher package.


Configure LLM

As described in the introduction, the default LLM and embedding is OpenAI due to its superior performance and speed. With that said, GPT Researcher supports various open/closed source LLMs and embeddings, and you can easily switch between them by updating the SMART_LLM, FAST_LLM and EMBEDDING env variables. You might also need to include the provider API key and corresponding configuration params.

Current supported LLMs are openai, anthropic, azure_openai, cohere, google_vertexai, google_genai, fireworks, ollama, together, mistralai, huggingface, groq, bedrock and litellm.

Current supported embeddings are openai, azure_openai, cohere, google_vertexai, google_genai, fireworks, ollama, together, mistralai, huggingface, nomic ,voyageai and bedrock.

To learn more about support customization options see here.

Please note: GPT Researcher is optimized and heavily tested on GPT models. Some other models might run into context limit errors, and unexpected responses. Please provide any feedback in our Discord community channel, so we can better improve the experience and performance.

Below you can find examples for how to configure the various supported LLMs.
OpenAI

# set the custom OpenAI API key
OPENAI_API_KEY=[Your Key]

# specify llms
FAST_LLM=openai:gpt-4o-mini
SMART_LLM=openai:gpt-4.1
STRATEGIC_LLM=openai:o4-mini

# specify embedding
EMBEDDING=openai:text-embedding-3-small

Custom LLM

Create a local OpenAI API using llama.cpp Server.

For custom LLM, specify "openai:{your-llm}"

# set the custom OpenAI API url
OPENAI_BASE_URL=http://localhost:1234/v1
# set the custom OpenAI API key
OPENAI_API_KEY=dummy_key

# specify custom llms  
FAST_LLM=openai:your_fast_llm
SMART_LLM=openai:your_smart_llm
STRATEGIC_LLM=openai:your_strategic_llm

For custom embedding, set "custom:{your-embedding}"

# set the custom OpenAI API url
OPENAI_BASE_URL=http://localhost:1234/v1
# set the custom OpenAI API key
OPENAI_API_KEY=dummy_key

# specify the custom embedding model   
EMBEDDING=custom:your_embedding

Azure OpenAI

In Azure OpenAI you have to chose which models you want to use and make deployments for each model. You do this on the Azure OpenAI Portal.

In January 2025 the models that are recommended to use are:

    gpt-4o-mini
    gpt-4o
    o1-preview or o1-mini (You might need to request access to these models before you can deploy them).

Please then specify the model names/deployment names in your .env file.

Required Precondition

    Your endpoint can have any valid name.
    A model's deployment name must be the same as the model name.
    You need to deploy an Embedding Model: To ensure optimal performance, GPT Researcher requires the 'text-embedding-3-large' model. Please deploy this specific model to your Azure Endpoint.

Recommended:

    Quota increase: You should also request a quota increase especially for the embedding model, as the default quota is not sufficient.

# set the azure api key and deployment as you have configured it in Azure Portal. There is no default access point unless you configure it yourself!
AZURE_OPENAI_API_KEY=[Your Key]
AZURE_OPENAI_ENDPOINT=https://&#123;your-endpoint&#125;.openai.azure.com/
OPENAI_API_VERSION=2024-05-01-preview

# each string is "azure_openai:deployment_name". ensure that your deployment have the same name as the model you use!
FAST_LLM=azure_openai:gpt-4o-mini
SMART_LLM=azure_openai:gpt-4o
STRATEGIC_LLM=azure_openai:o1-preview

# specify embedding
EMBEDDING=azure_openai:text-embedding-3-large

Add langchain-azure-dynamic-sessions to requirements.txt for Docker Support or pip install it
Ollama

GPT Researcher supports both Ollama LLMs and embeddings. You can choose each or both. To use Ollama you can set the following environment variables

OLLAMA_BASE_URL=http://localhost:11434
FAST_LLM=ollama:llama3
SMART_LLM=ollama:llama3
STRATEGIC_LLM=ollama:llama3

EMBEDDING=ollama:nomic-embed-text

Add langchain-ollama to requirements.txt for Docker Support or pip install it
Granite with Ollama

GPT Researcher has custom prompt formatting for the Granite family of models. To use the right formatting, you can set the following environment variables:

OLLAMA_BASE_URL=http://localhost:11434
FAST_LLM=ollama:granite3.3:2b
SMART_LLM=ollama:granite3.3:8b
STRATEGIC_LLM=ollama:granite3.3:8b
PROMPT_FAMILY=granite

Groq

GroqCloud provides advanced AI hardware and software solutions designed to deliver amazingly fast AI inference performance. To leverage Groq in GPT-Researcher, you will need a GroqCloud account and an API Key. (NOTE: Groq has a very generous free tier.)
Sign up

    You can signup here: https://console.groq.com/login

    Once you are logged in, you can get an API Key here: https://console.groq.com/keys

    Once you have an API key, you will need to add it to your systems environment using the variable name: GROQ_API_KEY=*********************

Update env vars

And finally, you will need to configure the GPT-Researcher Provider and Model variables:

GROQ_API_KEY=[Your Key]

# Set one of the LLM models supported by Groq
FAST_LLM=groq:Mixtral-8x7b-32768
SMART_LLM=groq:Mixtral-8x7b-32768
STRATEGIC_LLM=groq:Mixtral-8x7b-32768

Add langchain-groq to requirements.txt for Docker Support or pip install it

NOTE: As of the writing of this Doc (May 2024), the available Language Models from Groq are:

    Llama3-70b-8192
    Llama3-8b-8192
    Mixtral-8x7b-32768
    Gemma-7b-it

Anthropic

Refer to Anthropic Getting started page to obtain Anthropic API key. Update the corresponding env vars, for example:

ANTHROPIC_API_KEY=[Your Key]
FAST_LLM=anthropic:claude-2.1
SMART_LLM=anthropic:claude-3-opus-20240229
STRATEGIC_LLM=anthropic:claude-3-opus-20240229

Add langchain-anthropic to requirements.txt for Docker Support or pip install it

Anthropic does not offer its own embedding model, therefore, you'll want to either default to the OpenAI embedding model, or find another.
Mistral AI

Sign up for a Mistral API key. Then update the corresponding env vars, for example:

MISTRAL_API_KEY=[Your Key]
FAST_LLM=mistralai:open-mistral-7b
SMART_LLM=mistralai:mistral-large-latest
STRATEGIC_LLM=mistralai:mistral-large-latest

EMBEDDING=mistralai:mistral-embed

Add langchain-mistralai to requirements.txt for Docker Support or pip install it
Together AI

Together AI offers an API to query 50+ leading open-source models in a couple lines of code. Then update corresponding env vars, for example:

TOGETHER_API_KEY=[Your Key]
FAST_LLM=together:meta-llama/Llama-3-8b-chat-hf
SMART_LLM=together:meta-llama/Llama-3-70b-chat-hf
STRATEGIC_LLM=together:meta-llama/Llama-3-70b-chat-hf

EMBEDDING=mistralai:nomic-ai/nomic-embed-text-v1.5

Add langchain-together to requirements.txt for Docker Support or pip install it
HuggingFace

This integration requires a bit of extra work. Follow this guide to learn more. After you've followed the tutorial above, update the env vars:

HUGGINGFACE_API_KEY=[Your Key]
FAST_LLM=huggingface:HuggingFaceH4/zephyr-7b-beta
SMART_LLM=huggingface:HuggingFaceH4/zephyr-7b-beta
STRATEGIC_LLM=huggingface:HuggingFaceH4/zephyr-7b-beta

EMBEDDING=huggingface:sentence-transformers/all-MiniLM-L6-v2

Add langchain-huggingface to requirements.txt for Docker Support or pip install it
Google Gemini

Sign up here for obtaining a Google Gemini API Key and update the following env vars:

GOOGLE_API_KEY=[Your Key]
FAST_LLM=google_genai:gemini-1.5-flash
SMART_LLM=google_genai:gemini-1.5-pro
STRATEGIC_LLM=google_genai:gemini-1.5-pro

EMBEDDING=google_genai:models/text-embedding-004

Add langchain-google-genai to requirements.txt for Docker Support or pip install it
Google VertexAI

FAST_LLM=google_vertexai:gemini-1.5-flash-001
SMART_LLM=google_vertexai:gemini-1.5-pro-001
STRATEGIC_LLM=google_vertexai:gemini-1.5-pro-001

EMBEDDING=google_vertexai:text-embedding-004

Add langchain-google-vertexai to requirements.txt for Docker Support or pip install it
Cohere

COHERE_API_KEY=[Your Key]
FAST_LLM=cohere:command
SMART_LLM=cohere:command-nightly
STRATEGIC_LLM=cohere:command-nightly

EMBEDDING=cohere:embed-english-v3.0

Add langchain-cohere to requirements.txt for Docker Support or pip install it
Fireworks

FIREWORKS_API_KEY=[Your Key]
base_url=https://api.fireworks.ai/inference/v1/completions
FAST_LLM=fireworks:accounts/fireworks/models/mixtral-8x7b-instruct
SMART_LLM=fireworks:accounts/fireworks/models/mixtral-8x7b-instruct
STRATEGIC_LLM=fireworks:accounts/fireworks/models/mixtral-8x7b-instruct

EMBEDDING=fireworks:nomic-ai/nomic-embed-text-v1.5

Add langchain-fireworks to requirements.txt for Docker Support or pip install it
Bedrock

FAST_LLM=bedrock:anthropic.claude-3-sonnet-20240229-v1:0
SMART_LLM=bedrock:anthropic.claude-3-sonnet-20240229-v1:0
STRATEGIC_LLM=bedrock:anthropic.claude-3-sonnet-20240229-v1:0

EMBEDDING=bedrock:amazon.titan-embed-text-v2:0

Add langchain_aws to requirements.txt for Docker Support or pip install it
LiteLLM

FAST_LLM=litellm:perplexity/pplx-7b-chat
SMART_LLM=litellm:perplexity/pplx-70b-chat
STRATEGIC_LLM=litellm:perplexity/pplx-70b-chat

Add langchain_community to requirements.txt for Docker Support or pip install it
xAI

FAST_LLM=xai:grok-beta
SMART_LLM=xai:grok-beta
STRATEGIC_LLM=xai:grok-beta

Add langchain_xai to requirements.txt for Docker Support or pip install it
DeepSeek

DEEPSEEK_API_KEY=[Your Key]
FAST_LLM=deepseek:deepseek-chat
SMART_LLM=deepseek:deepseek-chat
STRATEGIC_LLM=deepseek:deepseek-chat

Openrouter.ai

OPENROUTER_API_KEY=[Your openrouter.ai key]
OPENAI_BASE_URL=https://openrouter.ai/api/v1
FAST_LLM=openrouter:google/gemini-2.0-flash-lite-001
SMART_LLM=openrouter:google/gemini-2.0-flash-001
STRATEGIC_LLM=openrouter:google/gemini-2.5-pro-exp-03-25
OPENROUTER_LIMIT_RPS=1  # Ratelimit request per secound
EMBEDDING=google_genai:models/text-embedding-004 # openrouter doesn't support embedding models, use google instead its free
GOOGLE_API_KEY=[Your *google gemini* key]

AI/ML API
AI/ML API provides 300+ AI models including Deepseek, Gemini, ChatGPT. The models run at enterprise-grade rate limits and uptimes.

You can check provider docs here

And models overview is here

AIMLAPI_API_KEY=[Your aimlapi.com key]
AIMLAPI_BASE_URL="https://api.aimlapi.com/v1"
FAST_LLM="aimlapi:claude-3-5-sonnet-20241022"
SMART_LLM="aimlapi:openai/o4-mini-2025-04-16"
STRATEGIC_LLM="aimlapi:x-ai/grok-3-mini-beta"
EMBEDDING="aimlapi:text-embedding-3-small"

vLLM

VLLM_OPENAI_API_KEY=[Your Key] # you can set this to 'EMPTY' or anything
VLLM_OPENAI_API_BASE=[Your base url] # for example http://localhost:8000/v1/
FAST_LLM=vllm_openai:Qwen/Qwen3-8B-AWQ
SMART_LLM=vllm_openai:Qwen/Qwen3-8B-AWQ
STRATEGIC_LLM=vllm_openai:Qwen/Qwen3-8B-AWQ

Other Embedding Models
Nomic

EMBEDDING=nomic:nomic-embed-text-v1.5

VoyageAI

VOYAGE_API_KEY=[Your Key]
EMBEDDING=voyageai:voyage-law-2

Add langchain-voyageai to requirements.txt for Docker Support or pip install it