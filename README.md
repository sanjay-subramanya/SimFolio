# SimFolio

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

An interactive financial analysis tool that enables you to test hypothetical market scenarios. Simulate price changes for individual stocks and watch how they ripple through your entire portfolio based on correlation patterns.

![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![Next.js](https://img.shields.io/badge/Next.js-15.4+-blue)

## 📊 Features

- **Instant Scenario Simulation**: Simulate stock price changes and see portfolio impact
- **Correlation-Based Modeling**: Account for how stocks move together in your portfolio
- **Component Analysis**: Clear overview of overall and individual stock effects

## 🧠 Architecture

A **Temporal Attention Graph Neural Network** that models stocks as nodes in a dynamic graph, where:

- **Graph Structure**: Stocks represent nodes, with edges weighted by historical correlations
- **Temporal Modeling**: Processes sequential price data to capture time-dependent patterns
- **Attention Mechanism**: Learns which historical time periods and stock relationships matter most for impact prediction

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Git

## 🚀 Getting Started

### Clone the Repository

```bash
git clone https://github.com/sanjay-subramanya/SimFolio.git
cd SimFolio
```

### Install Dependencies

1. **Backend Dependencies**

```bash
pip install -r backend/requirements.txt
```

2. **Frontend Dependencies**

```bash
cd frontend
npm install
cd ..
```

## 🔧 Running the Application

### Backend Server (API Endpoints)

Navigate to the backend directory and start the FastAPI server:

```bash
cd backend
uvicorn router:app --reload --port 8000
```

The server will start at port 8000 with API documentation available at http://127.0.0.1:8000/docs.

### Frontend Visualizer

Navigate to the frontend directory and start the development server:

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000. Ensure the backend server first is running to enable all features.

### Training Only

To train the network without the frontend interface:

```bash
cd backend
python main.py
```
