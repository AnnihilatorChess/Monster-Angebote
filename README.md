# Monster Energy Offers Tracker

This project consists of three components: a **data collection system**, a **website**, and an **email notification service**. Together, they track and display Monster Energy drink promotions across Austrian supermarkets.

## Key Features

### 1. Data Collection
- Aggregates Monster Energy offers from Austrian supermarket chains
- Collects product prices, validity dates, and supermarket chains
- Designed for daily automated updates

### 2. Website Portal
Visit: [monster-angebote.at](https://monster-angebote.at/)

**Website Structure:**
- **Homepage**: Displays current offers
- **Notifications Page**: User registration/deregistration and preference management for email alerts
- **Legal Pages**: Privacy policy (`/datenschutz`) and imprint (`/impressum`)
- Fully responsive design (mobile and desktop compatible)

### 3. Email Notification Service
- Sends automated alerts when new offers are detected
- Allows users to manage subscription preferences via email or website

## Technical Implementation

### Included Components
- **Website**: 
  - Frontend: HTML/CSS with minimal JavaScript
  - Backend: Python (Flask)
- **Email Service**: [`email_sender.py`](email_sender.py) (Python-based)
- **Database**: PostgreSQL hosted on Neon with tables:
  - `offers`: Individual promotions (price, dates, supermarket_id)
  - `supermarkets`: Chain names and retailer types (wholesaler/standard)
  - `emails`: Subscriber data and notification preferences

### Data Collection Note
The data collection implementation (`scraper.py`) is not included in this repository as it processes information from external sources. The system respects all applicable terms of service for data usage.

## Infrastructure
- **Backend**: Python (Flask)
- **Database**: Neon (PostgreSQL)
- **Hosting**: Render (web service + scheduled tasks)
- **Data Pipeline**: Automated daily updates

## How to Use
1. Visit [monster-angebote.at](https://monster-angebote.at/) to view current offers
2. Navigate to [Notifications Page](https://monster-angebote.at/benachrichtigungen) to manage email subscriptions
3. Use the unsubscribe link in any email to opt-out
