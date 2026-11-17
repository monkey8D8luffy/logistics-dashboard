> An interactive, responsive data visualization dashboard designed to uncover operational bottlenecks and optimize last-mile logistics performance. Developed for **LogiSight Analytics Pvt. Ltd.** (Mathematics for AI-II - FA-2 Assessment).

## 🌐 Live Deployment

**\[View the Live Dashboard Here\]**(https://logistics-dashboard-yxxpmb4tuemmkhybwteq7u.streamlit.app/)

## 📸 Dashboard Preview

><img width="1280" height="734" alt="image" src="https://github.com/user-attachments/assets/668d4b5d-459d-4d43-90a7-ef9da6e92a04" />


> 

## 🎯 Business Value & Use Case

This tool empowers logistics managers to interactively explore over **40,000 delivery records**. By transforming raw CSV data into actionable visual insights, stakeholders can:

* **Identify Regional Bottlenecks:** Pinpoint specific areas suffering from chronic delivery delays.

* **Optimize Fleet Allocation:** Compare the average delivery speeds of different vehicle types.

* **Manage Workforce:** Analyze the relationship between agent experience (age), performance ratings, and delivery speed.

* **Mitigate Weather/Traffic Impact:** Measure exactly how external variables degrade on-time delivery rates.

## ✨ Key Features & Visualizations

| Feature | Description | 
| ----- | ----- | 
| **🎨 "Liquid-Glass" UI** | A highly customized, responsive aesthetic utilizing CSS injection for a modern glassmorphism design. | 
| **🎛️ Interactive Control Deck** | Dynamic sliders allowing managers to test "What-if" speed-up scenarios and adjust the on-time SLA target live. | 
| **📊 Delay Analyzer** | Grouped bar charts comparing the direct impact of weather and traffic on delivery times. | 
| **🚚 Fleet Comparison** | Bar charts evaluating average delivery times across different vehicle types. | 
| **👥 Agent Insights** | Scatter plots mapping driver ratings against delivery speeds, segmented by age group. | 
| **🗺️ 3D Geospatial Map** | (Powered by PyDeck) An interactive map plotting delivery routes from store to drop-off, colored by duration severity. | 
| **🔍 Smart Sidebar** | Clean toggle pills and filters to instantly slice data by operational conditions. | 

## 🚀 Getting Started (Local Development)

To run this dashboard on your local machine:

1. **Clone the repository:**

   ```
   git clone https://github.com/monkey8D8luffy/logistics-dashboard.git
   cd logistics-dashboard
   
   ```

2. **Install the required dependencies:**

   ```
   pip install -r requirements.txt
   
   ```

3. **Run the Streamlit application:**

   ```
   streamlit run app.py
   
   ```

   *The dashboard will automatically open in your default web browser at `http://localhost:8501`.*
   
