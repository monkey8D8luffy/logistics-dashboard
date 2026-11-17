📦 Last-Mile Delivery Analytics Dashboard

A responsive, interactive data visualization dashboard built with Streamlit and Python to analyze last-mile logistics performance. This project was developed for the Logistics Analytics (FA-2) assessment.

🎯 Project Overview

This dashboard allows logistics managers at LogiSight Analytics Pvt. Ltd. to interactively explore a dataset of over 40,000 delivery records. By filtering through variables like weather, traffic conditions, vehicle types, and geographic zones, managers can quickly identify operational bottlenecks and make data-driven decisions to improve delivery speeds.

✨ Key Features

Custom "Liquid-Glass" UI: A highly customized, modern aesthetic utilizing CSS injection for a sleek glassmorphism design.

Interactive Control Deck: Dynamic sliders to test "What-if" speed-up scenarios and adjust the on-time SLA target live.

Dynamic Visualizations (Plotly):

Delay Analyzer: Grouped bar charts comparing the impact of weather and traffic.

Vehicle Comparison: Bar charts tracking average delivery times by fleet type.

Agent Performance: Scatter plots mapping driver ratings against delivery times.

Regional Heatmap: Density heatmap highlighting area-based delivery delays.

Category Boxplots: Distribution ranges for different product categories.

3D Geospatial Map (PyDeck): An interactive 3D map plotting delivery routes from store to drop-off, colored by delivery duration.

Smart Sidebar Filters: Clean toggle pills and dropdowns to drill down into specific operational conditions.

🛠️ Technology Stack

Python 3.x

Streamlit: Web application framework

Pandas: Data cleaning, grouping, and processing

Plotly Express / Graph Objects: Interactive charts

PyDeck: 3D Geospatial mapping

NumPy: Fast array calculations for live metrics

🚀 How to Run Locally

Clone the repository:

git clone https://github.com/monkey8D8luffy/logistics-dashboard.git
cd logistics-dashboard


Install the required dependencies:

pip install -r requirements.txt


Run the Streamlit application:

streamlit run app.py


The dashboard will automatically open in your default web browser at http://localhost:8501.

🌐 Live Deployment

This application is deployed live on Streamlit Community Cloud.
[View the Live Dashboard Here] (Add your Streamlit Cloud link here once deployed) 

Developed as part of the Mathematics for AI-II Formative Assessment (FA-2).
