import pandas as pd
import streamlit as st
from db import fetch_data

st.set_page_config(
    page_title="World Debt SQL Analytics",
    page_icon="🌐",
    layout="wide"
)

# SQL ANALYTICAL QUESTIONS REPOSITORY

QUERIES = {
    "Basic Queries": {
        "1. Retrieve all distinct country names": """
            SELECT DISTINCT country_name 
            FROM dim_countries 
            ORDER BY country_name ASC;
        """,
        "2. Count the total number of countries available": """
            SELECT COUNT(DISTINCT country_code) AS total_countries 
            FROM dim_countries;
        """,
        "3. Find the total number of indicators present": """
            SELECT COUNT(DISTINCT series_code) AS total_indicators 
            FROM dim_indicators;
        """,
        "4. Display the first 10 records of the dataset": """
            SELECT f.record_id, c.country_name, i.series_name, f.year, f.debt_value
            FROM fact_debt_data f
            JOIN dim_countries c ON f.country_code = c.country_code
            JOIN dim_indicators i ON f.series_code = i.series_code
            LIMIT 10;
        """,
        "5. Calculate the total global debt": """
            SELECT 
                SUM(debt_value) AS total_global_debt_raw,
                ROUND(SUM(debt_value) / 1e9, 2) AS total_global_debt_billions_usd
            FROM fact_debt_data;
        """,
        "6. List all unique indicator names": """
            SELECT DISTINCT series_name, topic 
            FROM dim_indicators 
            ORDER BY series_name ASC;
        """,
        "7. Find the number of records for each country": """
            SELECT c.country_name, COUNT(f.record_id) AS total_records
            FROM dim_countries c
            JOIN fact_debt_data f ON c.country_code = f.country_code
            GROUP BY c.country_name
            ORDER BY total_records DESC;
        """,
        "8. Display all records where debt is greater than 1 billion USD": """
            SELECT c.country_name, i.series_name, f.year, ROUND(f.debt_value / 1e9, 2) AS debt_billion_usd
            FROM fact_debt_data f
            JOIN dim_countries c ON f.country_code = c.country_code
            JOIN dim_indicators i ON f.series_code = i.series_code
            WHERE f.debt_value > 1e9
            ORDER BY f.debt_value DESC
            LIMIT 100;
        """,
        "9. Find the minimum, maximum, and average debt values": """
            SELECT 
                ROUND(MIN(debt_value) / 1e9, 4) AS min_debt_billion_usd,
                ROUND(MAX(debt_value) / 1e9, 2) AS max_debt_billion_usd,
                ROUND(AVG(debt_value) / 1e9, 2) AS avg_debt_billion_usd
            FROM fact_debt_data;
        """,
        "10. Count total number of records in the dataset": """
            SELECT COUNT(*) AS total_fact_records 
            FROM fact_debt_data;
        """
    },
    "Intermediate Level": {
        "11. Find the total debt for each country": """
            SELECT c.country_name, ROUND(SUM(f.debt_value) / 1e9, 2) AS total_debt_billion_usd
            FROM dim_countries c
            JOIN fact_debt_data f ON c.country_code = f.country_code
            GROUP BY c.country_name
            ORDER BY total_debt_billion_usd DESC;
        """,
        "12. Display the top 10 countries with the highest total debt": """
            SELECT c.country_name, c.region, ROUND(SUM(f.debt_value) / 1e9, 2) AS total_debt_billion_usd
            FROM dim_countries c
            JOIN fact_debt_data f ON c.country_code = f.country_code
            GROUP BY c.country_name, c.region
            ORDER BY total_debt_billion_usd DESC
            LIMIT 10;
        """,
        "13. Find the average debt per country": """
            SELECT c.country_name, ROUND(AVG(f.debt_value) / 1e9, 2) AS avg_debt_billion_usd
            FROM dim_countries c
            JOIN fact_debt_data f ON c.country_code = f.country_code
            GROUP BY c.country_name
            ORDER BY avg_debt_billion_usd DESC;
        """,
        "14. Calculate total debt for each indicator": """
            SELECT i.series_name, ROUND(SUM(f.debt_value) / 1e9, 2) AS total_debt_billion_usd
            FROM dim_indicators i
            JOIN fact_debt_data f ON i.series_code = f.series_code
            GROUP BY i.series_name
            ORDER BY total_debt_billion_usd DESC;
        """,
        "15. Identify the indicator contributing the highest total debt": """
            SELECT i.series_name, i.series_code, ROUND(SUM(f.debt_value) / 1e9, 2) AS total_debt_billion_usd
            FROM dim_indicators i
            JOIN fact_debt_data f ON i.series_code = f.series_code
            GROUP BY i.series_name, i.series_code
            ORDER BY total_debt_billion_usd DESC
            LIMIT 1;
        """,
        "16. Find the country with the lowest total debt": """
            SELECT c.country_name, c.region, ROUND(SUM(f.debt_value) / 1e6, 2) AS total_debt_million_usd
            FROM dim_countries c
            JOIN fact_debt_data f ON c.country_code = f.country_code
            GROUP BY c.country_name, c.region
            HAVING SUM(f.debt_value) > 0
            ORDER BY total_debt_million_usd ASC
            LIMIT 1;
        """,
        "17. Calculate total debt for each country and indicator combination": """
            SELECT c.country_name, i.series_name, ROUND(SUM(f.debt_value) / 1e9, 2) AS total_debt_billion_usd
            FROM fact_debt_data f
            JOIN dim_countries c ON f.country_code = c.country_code
            JOIN dim_indicators i ON f.series_code = i.series_code
            GROUP BY c.country_name, i.series_name
            ORDER BY c.country_name ASC, total_debt_billion_usd DESC;
        """,
        "18. Count how many indicators each country has": """
            SELECT c.country_name, COUNT(DISTINCT f.series_code) AS unique_indicators_count
            FROM dim_countries c
            JOIN fact_debt_data f ON c.country_code = f.country_code
            GROUP BY c.country_name
            ORDER BY unique_indicators_count DESC;
        """,
        "19. Display countries whose total debt is above the global average": """
            WITH CountryTotals AS (
                SELECT c.country_name, SUM(f.debt_value) AS country_total
                FROM dim_countries c
                JOIN fact_debt_data f ON c.country_code = f.country_code
                GROUP BY c.country_name
            ),
            GlobalBenchmark AS (
                SELECT AVG(country_total) AS avg_country_debt FROM CountryTotals
            )
            SELECT 
                ct.country_name,
                ROUND(ct.country_total / 1e9, 2) AS total_debt_billion_usd,
                ROUND(gb.avg_country_debt / 1e9, 2) AS global_avg_billion_usd
            FROM CountryTotals ct
            CROSS JOIN GlobalBenchmark gb
            WHERE ct.country_total > gb.avg_country_debt
            ORDER BY ct.country_total DESC;
        """,
        "20. Rank countries based on total debt (highest to lowest)": """
            SELECT 
                DENSE_RANK() OVER (ORDER BY SUM(f.debt_value) DESC) AS debt_rank,
                c.country_name,
                c.region,
                ROUND(SUM(f.debt_value) / 1e9, 2) AS total_debt_billion_usd
            FROM dim_countries c
            JOIN fact_debt_data f ON c.country_code = f.country_code
            GROUP BY c.country_name, c.region
            ORDER BY debt_rank ASC;
        """
    },
    "Advanced Level": {
        "21. Find the top 5 indicators contributing most to global debt": """
            SELECT 
                i.series_code,
                i.series_name,
                ROUND(SUM(f.debt_value) / 1e9, 2) AS total_debt_billion_usd
            FROM dim_indicators i
            JOIN fact_debt_data f ON i.series_code = f.series_code
            GROUP BY i.series_code, i.series_name
            ORDER BY total_debt_billion_usd DESC
            LIMIT 5;
        """,
        "22. Calculate percentage contribution of each country to total global debt": """
            SELECT 
                c.country_name,
                ROUND(SUM(f.debt_value) / 1e9, 2) AS country_debt_billion_usd,
                ROUND(
                    (SUM(f.debt_value) / (SELECT SUM(debt_value) FROM fact_debt_data)) * 100, 
                    2
                ) AS percentage_of_global_debt
            FROM dim_countries c
            JOIN fact_debt_data f ON c.country_code = f.country_code
            GROUP BY c.country_name
            ORDER BY percentage_of_global_debt DESC;
        """,
        "23. Identify the top 3 countries for each indicator based on debt": """
            WITH RankedCountryIndicators AS (
                SELECT 
                    i.series_name,
                    c.country_name,
                    ROUND(SUM(f.debt_value) / 1e9, 2) AS total_debt_billion_usd,
                    ROW_NUMBER() OVER(
                        PARTITION BY i.series_name 
                        ORDER BY SUM(f.debt_value) DESC
                    ) AS rnk
                FROM fact_debt_data f
                JOIN dim_countries c ON f.country_code = c.country_code
                JOIN dim_indicators i ON f.series_code = i.series_code
                GROUP BY i.series_name, c.country_name
            )
            SELECT series_name, rnk AS top_rank, country_name, total_debt_billion_usd
            FROM RankedCountryIndicators
            WHERE rnk <= 3
            ORDER BY series_name ASC, top_rank ASC;
        """,
        "24. Find the difference between maximum and minimum debt for each country": """
            SELECT 
                c.country_name,
                ROUND(MAX(f.debt_value) / 1e9, 2) AS max_debt_billion_usd,
                ROUND(MIN(f.debt_value) / 1e9, 2) AS min_debt_billion_usd,
                ROUND((MAX(f.debt_value) - MIN(f.debt_value)) / 1e9, 2) AS debt_spread_billion_usd
            FROM dim_countries c
            JOIN fact_debt_data f ON c.country_code = f.country_code
            GROUP BY c.country_name
            ORDER BY debt_spread_billion_usd DESC;
        """,
        "25. Top 10 countries with highest debt (View structure)": """
            SELECT 
                c.country_code,
                c.country_name,
                c.region,
                ROUND(SUM(f.debt_value) / 1e9, 2) AS total_debt_billion_usd
            FROM dim_countries c
            JOIN fact_debt_data f ON c.country_code = f.country_code
            GROUP BY c.country_code, c.country_name, c.region
            ORDER BY total_debt_billion_usd DESC
            LIMIT 10;
        """,
        "26. Categorize countries into High, Medium, Low Debt tiers": """
            WITH CountryAggregates AS (
                SELECT 
                    c.country_name, 
                    c.region, 
                    ROUND(SUM(f.debt_value) / 1e9, 2) AS total_debt_billion
                FROM dim_countries c
                JOIN fact_debt_data f ON c.country_code = f.country_code
                GROUP BY c.country_name, c.region
            )
            SELECT 
                country_name,
                region,
                total_debt_billion,
                CASE 
                    WHEN total_debt_billion >= 500 THEN 'High Debt (>= $500B)'
                    WHEN total_debt_billion BETWEEN 100 AND 499.99 THEN 'Medium Debt ($100B - $500B)'
                    ELSE 'Low Debt (< $100B)'
                END AS debt_category
            FROM CountryAggregates
            ORDER BY total_debt_billion DESC;
        """,
        "27. Use window functions to calculate cumulative debt per country": """
            SELECT 
                c.country_name,
                f.year,
                ROUND(SUM(f.debt_value) / 1e9, 2) AS yearly_debt_billion,
                ROUND(
                    SUM(SUM(f.debt_value)) OVER (
                        PARTITION BY c.country_name 
                        ORDER BY f.year 
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) / 1e9, 
                    2
                ) AS cumulative_debt_billion
            FROM fact_debt_data f
            JOIN dim_countries c ON f.country_code = c.country_code
            GROUP BY c.country_name, f.year
            ORDER BY c.country_name, f.year;
        """,
        "28. Find indicators where average debt is higher than overall average debt": """
            SELECT 
                i.series_name,
                ROUND(AVG(f.debt_value) / 1e9, 2) AS indicator_avg_billion
            FROM dim_indicators i
            JOIN fact_debt_data f ON i.series_code = f.series_code
            GROUP BY i.series_name
            HAVING AVG(f.debt_value) > (SELECT AVG(debt_value) FROM fact_debt_data)
            ORDER BY indicator_avg_billion DESC;
        """,
        "29. Identify countries contributing more than 5% of global debt": """
            WITH GlobalSummary AS (
                SELECT SUM(debt_value) AS global_total FROM fact_debt_data
            )
            SELECT 
                c.country_name,
                c.region,
                ROUND(SUM(f.debt_value) / 1e9, 2) AS country_debt_billion,
                ROUND((SUM(f.debt_value) / gs.global_total) * 100, 2) AS contribution_percentage
            FROM dim_countries c
            JOIN fact_debt_data f ON c.country_code = f.country_code
            CROSS JOIN GlobalSummary gs
            GROUP BY c.country_name, c.region, gs.global_total
            HAVING contribution_percentage > 5.0
            ORDER BY contribution_percentage DESC;
        """,
        "30. Find the most dominant indicator (highest contribution) for each country": """
            WITH CountryIndicatorRank AS (
                SELECT 
                    c.country_name,
                    i.series_name AS dominant_indicator,
                    ROUND(SUM(f.debt_value) / 1e9, 2) AS total_debt_billion,
                    ROW_NUMBER() OVER (
                        PARTITION BY c.country_name 
                        ORDER BY SUM(f.debt_value) DESC
                    ) AS rnk
                FROM fact_debt_data f
                JOIN dim_countries c ON f.country_code = c.country_code
                JOIN dim_indicators i ON f.series_code = i.series_code
                GROUP BY c.country_name, i.series_name
            )
            SELECT country_name, dominant_indicator, total_debt_billion
            FROM CountryIndicatorRank
            WHERE rnk = 1
            ORDER BY total_debt_billion DESC;
        """
    }
}

# MAIN PAGE USER INTERFACE

st.title("International Debt SQL Analytics")
st.write("---")

# Main page dropdown selectors
col1, col2 = st.columns([1, 2])

with col1:
    selected_tier = st.selectbox("📂 Select Query Level", list(QUERIES.keys()))

with col2:
    selected_question = st.selectbox("❓ Select Analytical Question", list(QUERIES[selected_tier].keys()))

raw_sql = QUERIES[selected_tier][selected_question].strip()

# Directly display the SQL query box
st.code(raw_sql, language="sql")

if st.button("Execute SQL Query"):
    with st.spinner("Fetching data from MySQL database..."):
        df_result = fetch_data(raw_sql)

    if not df_result.empty:
        st.success(f"Query executed successfully! ({len(df_result)} rows returned)")
        st.dataframe(df_result, use_container_width=True)
        
    else:
        st.warning("No records returned or failed to establish database connection.")