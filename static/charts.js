// charts.js - Premium SaaS Dynamic Charts
document.addEventListener('DOMContentLoaded', () => {
    // Check if we are on the dashboard
    const chartCanvas = document.getElementById('fleetChart');
    if (!chartCanvas) return;

    // Load Chart.js dynamically if not already loaded
    if (typeof Chart === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = initCharts;
        document.head.appendChild(script);
    } else {
        initCharts();
    }

    function initCharts() {
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.font.family = "'Cairo', sans-serif";

        const ctx = chartCanvas.getContext('2d');
        
        // Gradient for active drivers
        const gradientActive = ctx.createLinearGradient(0, 0, 0, 400);
        gradientActive.addColorStop(0, 'rgba(197, 160, 89, 0.8)');
        gradientActive.addColorStop(1, 'rgba(197, 160, 89, 0.2)');

        // Gradient for inactive drivers
        const gradientInactive = ctx.createLinearGradient(0, 0, 0, 400);
        gradientInactive.addColorStop(0, 'rgba(59, 130, 246, 0.8)');
        gradientInactive.addColorStop(1, 'rgba(59, 130, 246, 0.2)');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'],
                datasets: [
                    {
                        label: 'المركبات النشطة',
                        data: [65, 70, 80, 81, 86, 85],
                        backgroundColor: gradientActive,
                        borderRadius: 6,
                        borderWidth: 0
                    },
                    {
                        label: 'في الصيانة',
                        data: [12, 10, 8, 14, 7, 5],
                        backgroundColor: gradientInactive,
                        borderRadius: 6,
                        borderWidth: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#f8fafc',
                            font: { size: 14, family: "'Cairo', sans-serif" }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(11, 13, 20, 0.9)',
                        titleColor: '#c5a059',
                        bodyColor: '#fff',
                        borderColor: 'rgba(197, 160, 89, 0.3)',
                        borderWidth: 1,
                        padding: 12
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    }
});
