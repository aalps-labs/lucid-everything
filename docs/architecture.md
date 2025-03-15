# Lucid Everything Architecture

## System Overview

Lucid Everything is designed with a modular architecture that enables efficient news gathering, fact-checking, and multi-channel delivery.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Lucid Everything Agent                       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Request Processing                          │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   NEAR Hub      │    │    Twitter      │    │    AITP      │ │
│  │   Interface     │    │    Interface    │    │   Interface  │ │
│  └────────┬────────┘    └────────┬────────┘    └──────┬───────┘ │
│           │                      │                     │        │
│           └──────────────────────┼─────────────────────┘        │
│                                  │                              │
└──────────────────────────────────┼──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Core Processing                            │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │  News Gathering │    │  Summarization  │    │ Fact-Checking│ │
│  │     Engine      │───▶│     Engine      │───▶│    Engine    │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                 │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Response Generation                         │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │ Source Citation │    │ Format Adapters │    │  Delivery    │ │
│  │    Module       │───▶│  (HTML/Text)    │───▶│  Channels    │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Request Processing
- **NEAR Hub Interface**: Handles direct user interactions via the NEAR Agent Hub
- **Twitter Interface**: Processes mentions and requests via Twitter
- **AITP Interface**: Enables other NEAR agents to request summaries

### Core Processing
- **News Gathering Engine**: Collects news from reliable sources based on query
- **Summarization Engine**: Creates concise, accurate summaries using AI
- **Fact-Checking Engine**: Verifies information against multiple sources

### Response Generation
- **Source Citation Module**: Adds proper citations to all information
- **Format Adapters**: Converts summaries to appropriate formats (HTML, text)
- **Delivery Channels**: Sends responses through the appropriate channel

## Data Flow

1. User request received through one of the interfaces
2. Request analyzed to extract topic, timeframe, and other parameters
3. News gathering engine collects relevant articles from trusted sources
4. Summarization engine creates a concise summary
5. Fact-checking engine verifies information and adds confidence scores
6. Source citation module adds proper citations
7. Format adapter converts to appropriate output format
8. Response delivered through the original request channel

## Technology Stack

- **Backend**: Python with NEAR AI SDK
- **NLP**: Large Language Models for summarization and analysis
- **Data Storage**: Temporary caching for frequent requests
- **APIs**: Twitter API, News APIs, Web Search APIs
- **Deployment**: NEAR Agent Hub infrastructure 