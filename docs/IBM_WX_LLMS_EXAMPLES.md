# IBM WX-LLMs Powered Examples Documentation

## Overview

The IBM/wx-llms-powered-examples repository showcases the use of IBM foundation models, including IBM Granite 3.0, in combination with various AI concepts and techniques. These examples demonstrate how to leverage IBM's foundation models for different applications and use cases. <mcreference link="https://github.com/IBM/wx-llms-powered-examples" index="1">1</mcreference>

## Key Concepts and Technologies

### IBM Watsonx

Watsonx is IBM's AI and data platform that offers services to use foundation models, including Large Language Models (LLMs). It provides access to various IBM foundation models, such as the Granite series, as well as models from other providers like Meta and Mistral AI. <mcreference link="https://github.com/IBM/wx-llms-powered-examples" index="1">1</mcreference> <mcreference link="https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models.html?context=wx" index="4">4</mcreference>

### IBM Granite Models

The Granite series is IBM's family of foundation models designed for enterprise applications. The third generation, Granite 3.0, was released in October 2024 and is designed to balance power and practicality, offering state-of-the-art performance relative to its model size while prioritizing safety, speed, and cost-efficiency. <mcreference link="https://github.com/IBM/wx-llms-powered-examples" index="1">1</mcreference>

## Techniques Demonstrated

The repository showcases several advanced AI techniques that can be applied to our Smart Travel Planner application:

### Chain-of-Thought (CoT) Prompting

Chain-of-Thought prompting is a strategy that enhances the reasoning capabilities of LLMs by breaking down complex problems into smaller parts and solving them step by step. This technique can be valuable for our application when analyzing complex traffic patterns and making route recommendations. <mcreference link="https://github.com/IBM/wx-llms-powered-examples" index="1">1</mcreference>

### Reasoning & Acting (ReAct)

ReAct combines reasoning and acting with LLMs, allowing an AI Agent to take actions based on the results of the model's reasoning. Each subsequent reasoning step can be influenced by the outcome of the previous action, creating a feedback loop. This approach could be used in our application to iteratively refine route recommendations based on changing traffic conditions. <mcreference link="https://github.com/IBM/wx-llms-powered-examples" index="1">1</mcreference>

### Retrieval-Augmented Generation (RAG)

RAG is a technique that enhances LLM responses by retrieving relevant information from external sources before generating a response. The repository includes an example that illustrates how RAG can assist with question-answering tasks. In our Smart Travel Planner, RAG could be used to incorporate real-time traffic data and historical patterns into the AI's analysis. <mcreference link="https://github.com/IBM/wx-llms-powered-examples" index="1">1</mcreference>

### Tool Calling

Tool Calling refers to the ability of an LLM to interact with external tools, systems, or APIs to perform tasks that go beyond the model's internal capabilities. This concept allows LLMs to extend their functionality by leveraging external resources, enabling them to perform specialized tasks, retrieve information, or manipulate data in real-time. In our application, Tool Calling could be used to interact with the TomTom Traffic API and other external services. <mcreference link="https://github.com/IBM/wx-llms-powered-examples" index="1">1</mcreference>

## Relevant Examples for Smart Travel Planner

### wx-tech-support-agent

This example demonstrates an AI Agent designed to automate a technical support use case by guiding users through a troubleshooting process and taking appropriate actions when needed. It leverages techniques such as Chain-of-Thought (CoT) prompting and Reasoning & Acting (ReAct) using LangChain, along with multiple LLMs, including Granite 3.0 provided via watsonx. Additionally, it incorporates features like Chat Memory and Tool Calling to enhance functionality. <mcreference link="https://github.com/IBM/wx-llms-powered-examples" index="1">1</mcreference>

This example is particularly relevant to our Smart Travel Planner as it demonstrates how to create an interactive agent that can guide users through the process of planning their travel, analyzing traffic conditions, and making recommendations.

### wx-rag-with-granite3

This example illustrates how RAG can assist with question-answering tasks. It utilizes a public dataset, TechQA, to provide answers or information related to IBM products in response to user questions/queries. <mcreference link="https://github.com/IBM/wx-llms-powered-examples" index="1">1</mcreference>

For our Smart Travel Planner, a similar approach could be used to retrieve and incorporate relevant traffic data, historical patterns, and location-specific information to enhance the AI's analysis and recommendations.

## Integration with Vector Databases

The repository also includes an example (wx-weaviate-embedding-api) that demonstrates how to integrate Watsonx embedding models with Weaviate, an open-source vector database. This integration enables semantic search functionality, which could be valuable for our application when searching for similar traffic patterns or historical data. <mcreference link="https://github.com/IBM/wx-llms-powered-examples/blob/main/wx-weaviate-embedding-api/README.md" index="5">5</mcreference>

## Application to Smart Travel Planner

Based on the examples and techniques demonstrated in the IBM/wx-llms-powered-examples repository, we can enhance our Smart Travel Planner in the following ways:

1. **Improved Traffic Analysis**: Use Chain-of-Thought prompting to break down complex traffic analysis into step-by-step reasoning, providing more detailed and accurate insights.

2. **Dynamic Route Recommendations**: Implement ReAct to create a feedback loop where the AI can adjust its recommendations based on changing traffic conditions and user preferences.

3. **Enhanced Data Retrieval**: Use RAG to incorporate real-time traffic data, historical patterns, and location-specific information into the AI's analysis.

4. **External API Integration**: Leverage Tool Calling to interact with the TomTom Traffic API and other external services, extending the AI's capabilities beyond its internal knowledge.

5. **Semantic Search**: Integrate with vector databases like Weaviate to enable semantic search for similar traffic patterns or historical data.

## References

1. IBM/wx-llms-powered-examples GitHub Repository: [https://github.com/IBM/wx-llms-powered-examples](https://github.com/IBM/wx-llms-powered-examples)
2. IBM/llm-watsonx GitHub Repository: [https://github.com/IBM/llm-watsonx](https://github.com/IBM/llm-watsonx)
3. IBM/watsonx-data GitHub Repository: [https://github.com/IBM/watsonx-data](https://github.com/IBM/watsonx-data)
4. Supported foundation models in watsonx.ai: [https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models.html?context=wx](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models.html?context=wx)
5. wx-weaviate-embedding-api README: [https://github.com/IBM/wx-llms-powered-examples/blob/main/wx-weaviate-embedding-api/README.md](https://github.com/IBM/wx-llms-powered-examples/blob/main/wx-weaviate-embedding-api/README.md)