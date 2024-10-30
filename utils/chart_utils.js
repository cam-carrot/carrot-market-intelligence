function createSEOSnapshotChart(marketAnalysis) {
    const searchResults = marketAnalysis.search_results;
    const weBuyHousesResults = searchResults['we buy houses'] || [];
    
    // Process only top 10 results
    const chartData = weBuyHousesResults
        .slice(0, 10)
        .map(result => ({
            rank: result.rank,
            authority: result.domain in marketAnalysis.seo_metrics 
                ? marketAnalysis.seo_metrics[result.domain].authority_score 
                : 0,
            backlinks: result.domain in marketAnalysis.seo_metrics
                ? marketAnalysis.seo_metrics[result.domain].backlink_count
                : 0
        }))
        .sort((a, b) => a.rank - b.rank);  // Sort by rank ascending

    const ctx = document.getElementById('seoSnapshotChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.map(d => `Rank ${d.rank}`),
            datasets: [
                {
                    label: 'Authority Score',
                    yAxisID: 'y-authority',
                    data: chartData.map(d => d.authority),
                    backgroundColor: 'rgba(99, 102, 241, 0.7)',  // Indigo color
                    order: 2,
                    barPercentage: 0.6
                },
                {
                    label: 'Backlinks',
                    yAxisID: 'y-backlinks',
                    data: chartData.map(d => d.backlinks),
                    type: 'bar',  // Changed to bar
                    backgroundColor: 'rgba(34, 197, 94, 0.7)',  // Green color
                    order: 1,
                    barPercentage: 0.6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,  // Changed to true
            aspectRatio: 2,  // Added aspect ratio
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                'y-authority': {
                    type: 'linear',
                    position: 'left',
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Authority Score'
                    }
                },
                'y-backlinks': {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Number of Backlinks'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            },
            plugins: {
                title: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            return `${label}: ${context.datasetIndex === 1 ? value.toLocaleString() : value.toFixed(1)}`;
                        }
                    }
                }
            }
        }
    });
}