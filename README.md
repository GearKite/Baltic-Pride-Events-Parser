# Baltic Pride events parser

Parses the Baltic Pride website into an `.ics` file.

## Prerequisites

- A somewhat up-to-date version of Python. (Tested on 3.12)
- `wget`/`curl`/your favorite website download utility

## Installation

1. Create a virtual environment  
   `virtualenv .venv`
2. Activate the virtual environment  
   `source .venv/bin/activate`
3. Install dependencies  
   `pip install -r requirements.txt`

# Usage

1. Download the events page  
   `wget -O events.html https://balticpride.org/events-2024/` (URL might change)
2. Run the parser  
   `python main.py`
3. Import the generated `events.ics` into your calendar
