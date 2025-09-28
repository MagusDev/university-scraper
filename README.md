# University Professor Web Scraper

A Python desktop application for scraping university websites to find professors and their contact information based on research keywords.

## Features

- 🎯 Keyword-based professor search across multiple universities
- 🏫 University configuration management with custom selectors
- 📊 SQLite database storage for universities and professors
- 📋 Export data to CSV format
- 🔍 Filter professors by research areas
- 🌙 Dark theme UI using CustomTkinter
- 📧 Email template generation for contacting professors

## Installation

1. **Clone or download the project**

   ```bash
   git clone <repository-url>
   cd "Web scraper"
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

1. **Activate your virtual environment** (if using one)

   ```bash
   .venv\Scripts\activate  # On Windows
   ```

2. **Run the application**
   ```bash
   python UI.py
   ```

The application will open with a dark-themed GUI containing two main tabs: "Professors" and "Universities".

## Usage Guide

### 1. Adding University Configurations

Before scraping, you need to configure universities with the correct HTML selectors:

#### Step 1: Navigate to Universities Tab

- Click on the "Universities" tab in the application

#### Step 2: Fill University Information

- **Name**: University name (e.g., "MIT")
- **Department**: Department name (e.g., "Computer Science")
- **URL**: The faculty/staff listing page URL

#### Step 3: Configure HTML Selectors

You need to inspect the university's website to find the correct HTML elements:

##### Finding Modal Tag/Class (Professor List Items):

1. **Open the university's faculty page in your browser**
2. **Right-click on a professor's card/item** and select "Inspect Element"
3. **Look for the container element** that wraps each professor's information
4. **Note the tag name** (e.g., `div`, `article`, `li`) → This is your **Modal Tag**
5. **Note the class name** (e.g., `faculty-card`, `professor-item`) → This is your **Modal Class**

**Example:**

```html
<div class="faculty-member-card">
  <!-- Modal Tag: div, Modal Class: faculty-member-card -->
  <a href="/professor/john-doe">
    <h3>Dr. John Doe</h3>
    <p>Associate Professor</p>
  </a>
</div>
```

##### Finding Name Tag/Class (Professor's Name):

1. **Click on a professor's profile link** to go to their individual page
2. **Right-click on the professor's name** and select "Inspect Element"
3. **Note the tag name** (e.g., `h1`, `h2`, `span`) → This is your **Name Tag**
4. **Note the class name** (e.g., `professor-name`, `page-title`) → This is your **Name Class**

**Example:**

```html
<h1 class="professor-title">Dr. John Doe</h1>
<!-- Name Tag: h1, Name Class: professor-title -->
```

##### Finding Email Tag/Class (Professor's Email):

1. **On the professor's profile page, look for their email**
2. **Right-click on the email** and select "Inspect Element"
3. **Note the tag name** (e.g., `a`, `span`, `div`) → This is your **Email Tag**
4. **Note the class name** (e.g., `email-link`, `contact-email`) → This is your **Email Class**

**Example:**

```html
<a class="contact-email" href="mailto:john.doe@university.edu"
  >john.doe@university.edu</a
>
<!-- Email Tag: a, Email Class: contact-email -->
```

#### Step 4: Save Configuration

- Click **"Add New University"** to save the configuration
- The university will appear in the universities list

### 2. Selecting Universities for Scraping

1. **Select universities** from the top list by clicking on them
2. **Click "Add to Selection"** to move them to the "Selected Universities" list
3. Only universities in the selection list will be scraped

### 3. Scraping Professors

#### Step 1: Switch to Professors Tab

- Click on the "Professors" tab

#### Step 2: Enter Keywords

- In the text box, enter research keywords separated by:
  - Commas (`,`)
  - Semicolons (`;`)
  - New lines

**Example keywords:**

```
machine learning, artificial intelligence
computer vision; natural language processing
deep learning
neural networks
```

#### Step 3: Start Scraping

- Click the **"Scrape"** button
- The application will search through selected universities
- Progress will be shown in the log panel on the left
- Found professors will appear in the professors table

### 4. Managing Data

#### Filtering Professors

- Click **"Filter"** to show only professors with "research" or "lab" in their content

#### Deleting Records

- Select rows in either table
- Click **"Delete Selected"** to remove them

#### Exporting Data

- Use the **"Export Universities"** or **"Export Professors"** buttons in the sidebar
- Data will be saved as CSV files

## Configuration Examples

### Example 1: MIT EECS Faculty

```
Name: MIT
Department: EECS
URL: https://www.eecs.mit.edu/people/faculty-advisors/
Modal Tag: div
Modal Class: views-row
Name Tag: h1
Name Class: page-title
Email Tag: a
Email Class: email-link
```

### Example 2: Stanford CS Faculty

```
Name: Stanford
Department: Computer Science
URL: https://cs.stanford.edu/directory/faculty
Modal Tag: div
Modal Class: person-card
Name Tag: h2
Name Class: person-name
Email Tag: span
Email Class: email-address
```

## Troubleshooting

### Common Issues

1. **No professors found**: Check if your HTML selectors are correct
2. **Application crashes during scraping**: Some universities may have anti-bot protection
3. **Empty email fields**: The email selector might be incorrect or emails are not publicly displayed

### Tips for Better Results

- Test selectors on a few professor pages manually first
- Some universities load content dynamically (JavaScript) - this scraper works with static HTML only
- Be respectful with scraping frequency to avoid being blocked
- Check if the university has an official API or directory

## Database

The application uses SQLite database (`scaper_data.db`) with two tables:

- `universities`: Stores university configurations
- `professors`: Stores scraped professor information

## Requirements

See `requirements.txt` for all dependencies:

- customtkinter
- requests
- beautifulsoup4
- plyer

## Author

**Mohammad Abaeiani (MagusDev)**

## License

This project is for educational purposes. Please respect robots.txt files and website terms of service when scraping.
