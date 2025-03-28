import React, { useEffect, useState } from "react";
import axios from "axios";
import Plot from "react-plotly.js";

const Chart = () => {
    const [chartData, setChartData] = useState(null);

    useEffect(() => {
        axios.get("http://localhost:8000/chart") // Backend API endpoint
            .then(response => {
                setChartData(response.data);
            })
            .catch(error => {
                console.error("Error fetching chart data:", error);
            });
    }, []);

    return (
        <div>
            <h2>Stock Price Trends</h2>
            {chartData ? (
                <Plot data={chartData.data} layout={chartData.layout} />
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
};

export default Chart;