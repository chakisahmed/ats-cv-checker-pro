# ATS CV Checker Pro

Advanced AI-powered ATS (Applicant Tracking System) CV checker with ML-based analysis, skill taxonomy matching, and comprehensive scoring.

## Features

- **6-Component Scoring** - Keywords, Semantic, Skills, Experience, Formatting, Metrics
- **Skill Taxonomy Matching** - Recognizes related skills in the same category
- **Gap Analysis** - Identifies employment gaps, skill gaps, and ATS blockers
- **Rewrite Suggestions** - Actionable improvements for bullet points
- **Interactive Charts** - Radar charts and skill heatmaps with Plotly
- **PDF Export** - Professional analysis reports

## Tech Stack

| Component | Technology |
|-----------|------------|
| Web UI | Streamlit |
| NLP | spaCy (en_core_web_sm) |
| Semantic Matching | sentence-transformers (all-MiniLM-L6-v2) |
| PDF Parsing | PyPDF2 |
| DOCX Parsing | python-docx |
| Charts | Plotly |
| PDF Export | fpdf2 |

## Screenshots

<img width="1517" height="595" alt="image" src="https://github.com/user-attachments/assets/78e1ace3-92e4-40fa-84eb-f6fb88d62fb3" />

<img width="1521" height="672" alt="image" src="https://github.com/user-attachments/assets/8c8e14ce-b71f-42d5-a0db-a4d2421ad481" />

<img width="1138" height="632" alt="image" src="https://github.com/user-attachments/assets/36b84247-9964-4456-ae52-840d7cc2a023" />

<img width="1091" height="576" alt="image" src="https://github.com/user-attachments/assets/a5c9b058-8702-4b2c-a238-2f0c5709ca3b" />



## Installation

```bash
# Clone the repository
git clone https://github.com/chakisahmed/ats-cv-checker-pro.git
cd ats-cv-checker-pro

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

## Usage

```bash
# Run the application
streamlit run app.py

# Or run on a specific port
streamlit run app.py --server.port 8502
```

Then open http://localhost:8501 (or 8502) in your browser.

## How to Use

1. **Upload your CV** (PDF, DOCX, or TXT format)
2. **Paste the job description** from the listing
3. **Click Analyze** to get your ATS score
4. **Review the results** across 5 tabs:
   - Skills - Matching and missing skills
   - Gaps - Issues and priorities
   - Improvements - Bullet point suggestions
   - ATS Check - Compatibility score and checklist
   - Export - Download PDF report

## Project Structure

```
ats-cv-checker-pro/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── config/
│   └── skill_taxonomy.json     # Industry skill mappings
├── parsers/
│   ├── document_parser.py      # PDF/DOCX extraction
│   └── resume_parser.py        # ML-based entity extraction
├── analyzer/
│   ├── keyword_analyzer.py     # Keyword analysis
│   ├── semantic_analyzer.py    # Semantic similarity
│   ├── skill_matcher.py        # Taxonomy matching
│   ├── gap_analyzer.py         # Gap detection
│   └── scoring.py              # 6-component scoring
├── suggestions/
│   ├── rewriter.py             # Bullet improvements
│   └── optimizer.py            # ATS best practices
├── reports/
│   └── pdf_generator.py        # PDF export
└── ui/
    ├── components.py           # UI components
    └── charts.py               # Plotly visualizations
```

## Performance Optimizations

The application includes several optimizations for faster analysis:

- **Model Caching** - ML models are loaded once and cached across sessions using `@st.cache_resource`
- **Batch Encoding** - Multiple texts are encoded in a single call for efficiency
- **Progress Tracking** - Visual progress bar shows analysis stages in real-time
- **TF-IDF Fallback** - Lightweight fallback when sentence-transformers can't load

## Future Roadmap

### Planned Enhancements

- **Database Persistence** - Save analysis results for version comparison
- **Task Queue Architecture** - For high-volume deployments:
  - Frontend: Accept uploads → Send job tickets to queue
  - Middleware: Redis/RabbitMQ for ticket management
  - Workers: Separate processes for ML analysis
  - Benefits: Non-blocking UI, horizontal scaling, better resource utilization

## License

MIT License
