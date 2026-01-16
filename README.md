# Hyper-Realistic AI Personas: Capstone Project

A 20-week capstone course developing emotionally intelligent, context-aware AI personas using advanced language models and agentic frameworks.

**Industry Partner:** Leidos  
**Course Duration:** 20 weeks  
**Focus:** Building functional AI persona systems with natural, contextually appropriate interactions

---

## Project Overview

This capstone project explores the cutting edge of conversational AI by developing hyper-realistic digital personas capable of:
- Natural, emotionally intelligent conversations
- Context-aware interactions across diverse scenarios
- Integration with external tools and data sources
- Measurable performance through rigorous evaluation metrics

Students work in teams to design, implement, and evaluate AI persona systems that demonstrate real-world applicability in domains such as customer service, education, healthcare, and entertainment.

---

## Key Technologies

- **Domain Adaptive Training (DAPT):** Continuing pre-training on domain-specific text to customize persona behavior and knowledge
- **Model Context Protocol (MCP):** Standard for connecting AI systems to external tools and data sources
- **Streamlit:** Framework for building interactive agentic user interfaces
- **Large Language Models:** Foundation models (Claude, GPT, etc.) as the base for persona development
- **Vector Databases:** For efficient persona memory and context retrieval

---

## Course Structure

### Phase 1: Foundation & Persona Development (Weeks 1-10)
- Research and design thinking
- Persona specification and use case definition
- Data collection and curation pipelines
- Domain adaptive training implementation
- Initial persona prototyping

### Phase 2: Agentic UI Platform (Weeks 11-15)
- MCP tool integration and API development
- Streamlit-based conversational interface
- Multi-turn dialogue management
- Memory and context handling
- System integration and testing

### Phase 3: Evaluation & Refinement (Weeks 16-20)
- Metrics development and implementation
- Human evaluation studies
- Performance benchmarking
- Final system optimization
- Presentation and demonstration

---

## Repository Structure

```
capstone/
├── README.md
├── docs/                           # Documentation
│   ├── project-requirements.md
│   ├── technology-stack.md
│   └── weekly-objectives.md
├── personas/                       # Persona development workstream
│   ├── specifications/             # Persona design documents
│   ├── datasets/                   # Training and evaluation data
│   ├── training/                   # DAPT scripts and configs
│   └── prototypes/                 # Early persona implementations
├── platform/                       # Agentic UI workstream
│   ├── mcp-tools/                  # MCP integrations
│   ├── ui/                         # Streamlit applications
│   ├── api/                        # Backend services
│   └── tests/                      # Integration tests
├── evaluation/                     # Metrics workstream
│   ├── metrics/                    # Evaluation code
│   ├── benchmarks/                 # Benchmark datasets
│   ├── results/                    # Evaluation outputs
│   └── analysis/                   # Performance analysis
├── resources/                      # Shared resources
│   ├── papers/                     # Research papers
│   ├── tutorials/                  # Learning materials
│   └── templates/                  # Code templates
└── deliverables/                   # Weekly submissions
    ├── week-04/
    ├── week-05/
    └── ...
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- API keys for LLM providers (Claude, OpenAI, etc.)
- Git and GitHub account
- Basic understanding of NLP and conversational AI

### Installation

```bash
# Clone the repository
git clone https://github.com/greg-katsios/capstone.git
cd capstone

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---

## Weekly Deliverables

Each week, teams submit:
- **Technical implementation** (code, configs, data)
- **Documentation** (design decisions, challenges, next steps)
- **Demo/Prototype** (working demonstration of progress)

See [docs/weekly-objectives.md](docs/weekly-objectives.md) for detailed requirements.

---

## Industry Partnership

### Leidos Collaboration
- **Weekly Mentor Calls:** Regular check-ins with industry mentors
- **Office Visit:** Hands-on experience at Leidos San Diego office
- **Real-World Focus:** Projects designed for practical applicability
- **Career Opportunities:** Potential internship and employment pathways

---

## Resources

### Research Papers
- Domain Adaptive Pre-training
- Persona-based conversational AI
- MCP and tool integration
- Evaluation methodologies for dialogue systems

### Technology Documentation
- [Anthropic MCP Documentation](https://docs.anthropic.com/mcp)
- [Streamlit Documentation](https://docs.streamlit.io)
- [LangChain Agent Framework](https://python.langchain.com/docs/agents)

### Tutorials
- Building your first AI persona
- Implementing DAPT with Hugging Face
- Creating MCP tools
- Deploying Streamlit applications

---

## Contributing

### Team Workflow
1. Create feature branch from `main`
2. Implement changes with clear commit messages
3. Submit pull request with description
4. Code review by at least one team member
5. Merge after approval

### Code Standards
- Follow PEP 8 for Python code
- Include docstrings for functions and classes
- Write unit tests for core functionality
- Update documentation with changes

---

## License

This project is created for educational purposes as part of the capstone course.
